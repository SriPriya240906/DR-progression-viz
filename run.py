from model import predict

image_path = r"C:\Users\msrip\OneDrive\Desktop\DR-ProgressionViz\dataset\train\000c1434d8d7.png"

result = predict(image_path)

print("Predicted DR Grade:", result)