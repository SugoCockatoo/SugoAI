import torch

# Cargar el modelo
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Contar los parámetros
total_params = sum(p.numel() for p in model.parameters())
print(f"Total number of parameters: {total_params}")

# Estimar el tamaño en bytes
size_in_bytes = total_params * 4
print(f"Estimated size in bytes: {size_in_bytes}")