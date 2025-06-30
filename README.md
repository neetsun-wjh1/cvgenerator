For Lambda function deployment, compile the libary files into a python folder, specifiying version 3.13
- pip install -r requirements.txt --platform manylinux2014_x86_64 --target python/ --only-binary=:all: --python-version 3.13!

test_lambda.py is to mock the run of lambda function. 
