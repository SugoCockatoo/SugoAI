import tensorflow as tf

# Set the correct path to your saved model directory using raw string
saved_model_dir = r"C:\Users\betas\yolov5\yolov5n_saved_model"

# Load the SavedModel
model = tf.saved_model.load(saved_model_dir)

# Convert the model to a TFLite format with quantization
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save the quantized model
with open("quantized_model.tflite", "wb") as f:
    f.write(tflite_model)

print("Quantized model saved as 'quantized_model.tflite'")
