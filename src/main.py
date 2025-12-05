from functions import recursive_directory_copy,generate_page
import os
import shutil

def main():
    """Delete everything in the  public directory
    """
    public_dir = os.path.join(os.getcwd(), "public")
    if os.path.exists(public_dir):
        for filename in os.listdir(public_dir):
            file_path = os.path.join(public_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"Removed file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Removed directory: {file_path}")
    """Copy all the static files from static to public"""
    static_dir = os.path.join(os.getcwd(), "static")
    if os.path.exists(static_dir):
        recursive_directory_copy(static_dir, public_dir)
    
    """Generate a page from content/index.md using template.html and write it to public/index.html"""
    content_path = os.path.join(os.getcwd(), "content", "index.md")
    template_path = os.path.join(os.getcwd(), "template.html")
    output_path = os.path.join(public_dir, "index.html")
    print(f"Generating page at: {output_path}")
    generate_page(content_path, template_path, output_path)
    

if __name__ == "__main__":
    main()