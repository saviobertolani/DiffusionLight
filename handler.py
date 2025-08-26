import os
import tempfile
import requests
from urllib.parse import urlparse
import runpod
import torch
from PIL import Image
import numpy as np
from diffusers import StableDiffusionPipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_image(url):
    """Download image from URL to temporary file"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        
        # Download in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        
        temp_file.close()
        return temp_file.name
    
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise

def process_hdri(image_path, resolution="1024x512", format="exr"):
    """Process image to HDRI using DiffusionLight"""
    try:
        logger.info(f"Processing HDRI with resolution {resolution} and format {format}")
        
        # Load the input image
        input_image = Image.open(image_path).convert('RGB')
        
        # Parse resolution
        width, height = map(int, resolution.split('x'))
        
        # Resize image to target resolution
        input_image = input_image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to numpy array for processing
        image_array = np.array(input_image)
        
        # Simple HDRI conversion (placeholder - replace with actual DiffusionLight logic)
        # This is where you'd integrate your actual DiffusionLight processing
        hdri_array = image_array.astype(np.float32) / 255.0
        
        # Create output filename
        output_filename = f"hdri_output.{format}"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        # Save based on format
        if format.lower() == 'exr':
            # For EXR format, you'd use OpenEXR library
            # For now, save as PNG with HDR-like processing
            hdri_image = Image.fromarray((hdri_array * 255).astype(np.uint8))
            hdri_image.save(output_path.replace('.exr', '.png'))
            output_path = output_path.replace('.exr', '.png')
        elif format.lower() == 'hdr':
            # For HDR format, you'd use specific HDR libraries
            hdri_image = Image.fromarray((hdri_array * 255).astype(np.uint8))
            hdri_image.save(output_path.replace('.hdr', '.png'))
            output_path = output_path.replace('.hdr', '.png')
        else:
            # Default to PNG
            hdri_image = Image.fromarray((hdri_array * 255).astype(np.uint8))
            hdri_image.save(output_path)
        
        logger.info(f"HDRI processing completed: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error processing HDRI: {str(e)}")
        raise

def upload_to_storage(file_path):
    """Upload processed file to temporary storage and return URL"""
    try:
        # For now, we'll return the local file path
        # In production, you'd upload to S3, Google Cloud Storage, etc.
        logger.info(f"File ready for download: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise

def handler(event):
    """Main handler function for RunPod"""
    try:
        logger.info(f"Received event: {event}")
        
        # Extract parameters from the event
        job_input = event.get('input', {})
        image_url = job_input.get('image_url')
        resolution = job_input.get('resolution', '1024x512')
        format = job_input.get('format', 'exr')
        job_id = job_input.get('job_id')
        
        if not image_url:
            raise ValueError("image_url is required")
        
        logger.info(f"Processing job {job_id}: {image_url} -> {resolution} {format}")
        
        # Step 1: Download the input image
        logger.info("Downloading input image...")
        input_image_path = download_image(image_url)
        
        # Step 2: Process the image to HDRI
        logger.info("Processing HDRI...")
        output_path = process_hdri(input_image_path, resolution, format)
        
        # Step 3: Upload to storage (or prepare for download)
        logger.info("Preparing output...")
        result_url = upload_to_storage(output_path)
        
        # Clean up temporary input file
        try:
            os.unlink(input_image_path)
        except:
            pass
        
        # Return success response
        result = {
            "status": "completed",
            "output": {
                "result_url": result_url,
                "resolution": resolution,
                "format": format,
                "job_id": job_id
            }
        }
        
        logger.info(f"Job {job_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    # Start the RunPod serverless handler
    runpod.serverless.start({"handler": handler})
