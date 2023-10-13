#BUILD STAGE USING PYTHON 3.8
FROM python:3.8

# Set the working directory inside the container
WORKDIR /

COPY ./ ./

#Upgrade Pip
RUN pip install --upgrade pip

# Install virtualenv
RUN pip install virtualenv

# Remove the existing virtual environment if it exists
RUN rm -rf venv

# Create a virtual environment
RUN virtualenv venv --python=python3.8

# Activate the virtual environment
RUN /bin/bash -c "source venv/bin/activate"

# Install cmake and dlib inside the virtual environment
RUN /bin/bash -c "source venv/bin/activate && pip install cmake dlib"

# Install the Python dependencies from requirements.txt
RUN /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
