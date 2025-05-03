from transformers import TrOCRProcessor, VisionEncoderDecoderModel, Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import load_dataset, Dataset
from PIL import Image
import torch

# Load processor dan model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Set tokenizer decoder config
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.vocab_size = model.decoder.config.vocab_size
model.config.eos_token_id = processor.tokenizer.eos_token_id

# Load dataset lokal (buat Dataset dari list dict)
import pandas as pd
df = pd.read_csv("labels.csv")

def encode_example( ):
    image = Image.open(f"images/{example['filename']}").convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values[0]
    labels = processor.tokenizer(example["text"], padding="max_length", max_length=128, truncation=True).input_ids
    labels = [l if l != processor.tokenizer.pad_token_id else -100 for l in labels]
    
    # Debugging: Print extracted values
    print("Extracted pixel_values:", pixel_values.shape)
    print("Original text:", example["text"])
    print("Tokenized labels:", labels)
    
    return {"pixel_values": pixel_values, "labels": torch.tensor(labels)}

dataset = Dataset.from_pandas(df)
dataset = dataset.map(encode_example)

# Training args
training_args = Seq2SeqTrainingArguments(
    output_dir="./trocr-finetuned",
    per_device_train_batch_size=2,
    num_train_epochs=5,
    logging_dir="./logs",
    save_strategy="epoch",
    evaluation_strategy="no",
    fp16=True if torch.cuda.is_available() else False
)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
