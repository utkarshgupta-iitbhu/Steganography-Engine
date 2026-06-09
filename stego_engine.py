import random
from PIL import Image

class StegoEngine:
    
    def __init__(self):
        self.HEADER_BITS = 32 #This represents the header size which tells the decoder how long the hidden file is

    def _to_bits(self, data: bytes) -> str:
        return ''.join([f"{b:08b}" for b in data]) #Converts the raw bytes into strings of 1 and 0. 08 refers to padding front with 0 to make the byte 8 character long
        
    def _to_bytes(self, bit_string: str) -> bytes:
        return bytes([int(bit_string[i:i+8], 2) for i in range(0, len(bit_string), 8)]) #Takes 8 characters continuosly and converts back to bytes

    def encode(self, image_path: str, payload: bytes, output_path: str, seed: str = None):
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        total_pixels = width * height
        
        max_bits = total_pixels * 3 #Each pixel has 3 color channels RGB and we alter 1 bit per color
        max_allowed_bytes = (max_bits - self.HEADER_BITS) // 8 #Removing the 32 bits used by headers and then dividing to get the bytes.
        
        if len(payload) > max_allowed_bytes:
            raise ValueError(f"CRITICAL: Payload ({len(payload)} bytes) exceeds the absolute limit of this image ({max_allowed_bytes} bytes).")
            
        payload_len = len(payload)
        header_bytes = payload_len.to_bytes(4, byteorder='big')
        
        master_bits = self._to_bits(header_bytes + payload)
        
        pixel_map = list(range(total_pixels))
        
        if seed:
            random.Random(seed).shuffle(pixel_map) #If a password is provided, we use it to get Pseudo Random Number

        bit_idx = 0 # Tracks which bit from master_bits we are currently hiding
        for i in range(len(pixel_map)):
            if bit_idx >= len(master_bits):
                break
            #X,Y coords of the pixel got 
            x = pixel_map[i] % width
            y = pixel_map[i] // width
            
            # Read the current colors of the target pixel
            r, g, b = pixels[x, y]
            
            #0xFE is Hexadecimal for binary 11111110. Doing a & with it keeps the first 7 bits same but sets the last bit to 0. Doing a | we drop our secret bit into the 8th bit.
            if bit_idx < len(master_bits):
                r = (r & 0xFE) | int(master_bits[bit_idx])
                bit_idx += 1
            if bit_idx < len(master_bits):
                g = (g & 0xFE) | int(master_bits[bit_idx])
                bit_idx += 1
            if bit_idx < len(master_bits):
                b = (b & 0xFE) | int(master_bits[bit_idx])
                bit_idx += 1
                
            pixels[x, y] = (r, g, b)
            
        img.save(output_path, format="PNG") #We force the output to be PNG as it is lossless compression

    def decode(self, image_path: str, seed: str = None) -> bytes:
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        total_pixels = width * height
        
        pixel_map = list(range(total_pixels))
        if seed:
            random.Random(seed).shuffle(pixel_map) #Seeding generates the same exact shuffled list
            
        extracted_bits = []
        payload_len = 0
        
        total_target_bits = self.HEADER_BITS #1st target is to get the header to know the length of the payload
        
        for i in range(total_pixels):
            if len(extracted_bits) >= total_target_bits:
                break
                
            x = pixel_map[i] % width
            y = pixel_map[i] // width
            r, g, b = pixels[x, y]
            
            #Doing a & with 1 gives the LSB
            extracted_bits.append(str(r & 1))
            extracted_bits.append(str(g & 1))
            extracted_bits.append(str(b & 1))
            
            if payload_len == 0 and len(extracted_bits) >= self.HEADER_BITS:
                header_str = ''.join(extracted_bits[:self.HEADER_BITS])
                payload_len = int(header_str, 2)
                total_target_bits = self.HEADER_BITS + (payload_len * 8) #We get the payload length total
                
        final_bits = ''.join(extracted_bits[self.HEADER_BITS : self.HEADER_BITS + (payload_len * 8)]) #Remove the header bits leaving the extracted payload
        
        return self._to_bytes(final_bits)

    def deep_scan_dump(self, image_path: str) -> bytes:
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        
        extracted_bits = []
        
        #We simply move top to bottom and left to right rather than a pixelmap
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                extracted_bits.append(str(r & 1))
                extracted_bits.append(str(g & 1))
                extracted_bits.append(str(b & 1))
                
        valid_bits_length = len(extracted_bits) - (len(extracted_bits) % 8)
        final_bits = ''.join(extracted_bits[:valid_bits_length])
        
        return self._to_bytes(final_bits)