# Base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment.yml to the container
COPY environment.yml .

# Install the Conda environment
RUN conda env create -f environment.yml

# Activate the environment and ensure it is activated by default
RUN echo "source activate photobusiness" > ~/.bashrc
ENV PATH=/opt/conda/envs/photobusiness/bin:$PATH

# Copy project files into the container
COPY photobeam .

# Expose the Django development server port
EXPOSE 8000

# Set the entry point to run the server
CMD ["bash", "-c", "source activate photobusiness && python manage.py collectstatic && python manage.py compress && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
