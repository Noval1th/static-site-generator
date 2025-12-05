# hello world
from funcs import copy_directory_contents, generate_pages_recursive
import os
import shutil

def main():
    # Get project paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    # Step 1: Delete anything in the public directory
    if os.path.exists(public_dir):
        print(f"Deleting public directory: {public_dir}")
        shutil.rmtree(public_dir)
    
    # Step 2: Copy all static files from static to public
    if os.path.exists(static_dir):
        print("Copying static files to public directory...")
        copy_directory_contents(static_dir, public_dir)
        print("Static files copied successfully!")
    else:
        print(f"Warning: Static directory not found: {static_dir}")
        # Create public directory anyway for the HTML pages
        os.makedirs(public_dir)
    
    # Step 3: Generate pages recursively from content directory
    if os.path.exists(content_dir) and os.path.exists(template_path):
        print("\nGenerating pages recursively from content directory...")
        generate_pages_recursive(content_dir, template_path, public_dir)
        print("\nSite generation complete!")
    else:
        if not os.path.exists(content_dir):
            print(f"Error: Content directory not found: {content_dir}")
        if not os.path.exists(template_path):
            print(f"Error: Template file not found: {template_path}")
    
    
if __name__ == "__main__":
    main()