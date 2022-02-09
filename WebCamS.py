import time

import cv2
import boto3

start_time = time.time()
camera = cv2.VideoCapture(0)
s3 = boto3.client(
    's3',
    aws_access_key_id="XXXXX",
    aws_secret_access_key="XXXXX",
    aws_session_token="XXXXX"
)

while True:
    return_value,image = camera.read()
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    cv2.imshow('image',gray)
    if cv2.waitKey(1)& 0xFF == ord('q'):
        break
    if time.time() - start_time >= 360:
        image_string = cv2.imencode('.jpg', image)[1].tostring()
        imageName = str(time.strftime("%Y_%m_%d_%H_%M")) + '.jpg'
        s3.put_object(Bucket="imagebucket14062696", Key=imageName, Body=image_string)
        start_time = time.time()

camera.release()
cv2.destroyAllWindows()