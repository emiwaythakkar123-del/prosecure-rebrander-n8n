import fitz
import sys
import os
import glob

def replace_logo(pdf_input, logo_path, position="right", output_path=None):
    # Handle input: string path or stream
    if isinstance(pdf_input, str):
        doc = fitz.open(pdf_input)
    else:
        # Assume stream (bytes or file-like)
        # If it's bytes
        if isinstance(pdf_input, bytes):
            doc = fitz.open(stream=pdf_input, filetype="pdf")
        else:
            # File-like object (e.g. Streamlit UploadedFile)
            # Streamlit UploadedFile works as a stream, but fitz might need read().
            # Safer to read to bytes.
            doc = fitz.open(stream=pdf_input.read(), filetype="pdf")
            pdf_input.seek(0) # Reset stream if needed elsewhere


    for page in doc:
        # Identify the rect to replace
        target_rect = None
        
        # Look for images on this page
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            # Get rects for this image
            rects = page.get_image_rects(xref)
            for rect in rects:
                if rect.width < 50 or rect.height < 20:
                    continue
                center_x = (rect.x0 + rect.x1) / 2
                
                if position == "right":
                    if center_x > 500: # It's on the right side
                        target_rect = rect
                        break
                elif position == "left":
                    if center_x < 500: # It's on the left side
                        target_rect = rect
                        break
            if target_rect:
                break
        
        if target_rect:
            # 1. Redact the old logo (draw white box)
            page.draw_rect(target_rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # 2. Insert new logo
            # Check if logo_path is a valid path or bytes
            if isinstance(logo_path, str):
                page.insert_image(target_rect, filename=logo_path, keep_proportion=True)
            else:
                 # Assume stream/bytes
                 page.insert_image(target_rect, stream=logo_path, keep_proportion=True)
                 
            print(f"  Replaced logo on page {page.number + 1} at {target_rect}")
        else:
            print(f"  WARNING: No candidate logo found for 'position={position}' on page {page.number + 1}")

        # --- Text Replacement ---
        # Background color sampled from PDF: (212, 153, 57) -> Normalized: (0.831, 0.6, 0.224)
        bg_color = (212/255, 153/255, 57/255)
        new_url = "http://www.bhaveshthakkar.com"
        
        # Search for the website text
        text_instances = page.search_for("www.prudentcorporate.com")
        for inst in text_instances:
            # 1. Redact the old text with the MATCHING background color
            page.draw_rect(inst, color=bg_color, fill=bg_color)
            
            # 2. Insert the new text
            rc = inst
            page.insert_text(
                point=fitz.Point(rc.x0, rc.y1 - 2), 
                text="www.bhaveshthakkar.com",
                fontsize=11, 
                fontname="helv", 
                color=(1, 1, 1) 
            )
            
            # 3. Handle Links
            links = page.get_links()
            for l in links:
                if fitz.Rect(l["from"]).intersects(inst):
                   page.delete_link(l) # clean up old link

            # Add new link
            page.insert_link(
                {"kind": fitz.LINK_URI, "from": inst, "uri": new_url}
            )
            
            print(f"  Replaced text and link on page {page.number + 1} at {inst} with bg={bg_color}")


    if output_path:
        doc.save(output_path)
        print(f"Saved to {output_path}")
    
    return doc.tobytes()

if __name__ == "__main__":
    pdf_files = glob.glob("*.pdf")
    logo_files = glob.glob("*.png")
    
    if not pdf_files or not logo_files:
        print("Error: PDF or PNG files not found.")
        sys.exit(1)
        
    # Pick a PDF that isn't an output file
    candidates = [f for f in pdf_files if "output" not in f and "Rebranded" not in f]
    if not candidates:
        # Fallback to checking specifically for the sample
        candidates = ["Prudent_Morning_Coffee_-_13th_Feb_2026.pdf"]
    
    pdf_path = candidates[0]
    logo_path = logo_files[0]
    
    # Default to right side logo replacement as per user preference
    replace_logo(pdf_path, logo_path, "right", "Prudent_Morning_Coffee_Rebranded.pdf")
