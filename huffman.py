import heapq
import os
from collections import defaultdict

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq
    
    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, Node):
            return False
        return self.freq == other.freq
    
class Huffman:
    def __init__(self, path):
        self.path = path
        self.__heap = []
        self.__codes = {}
        self.__reverse_mapping = {}
    
    def __make_frequency_dict(self, text):
        frequency = defaultdict(int)
        for char in text:
            frequency[char] += 1
        return frequency
    
    def __make_heap(self, frequency):
        for key in frequency:
            node = Node(key, frequency[key])
            heapq.heappush(self.__heap, node)
    
    def __merge_nodes(self):
        while len(self.__heap) > 1:
            node1 = heapq.heappop(self.__heap)
            node2 = heapq.heappop(self.__heap)
            
            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            heapq.heappush(self.__heap, merged)
    
    def __make_codes_helper(self, root, current_code):
        if root is None:
            return
        
        if root.char is not None:
            self.__codes[root.char] = current_code
            self.__reverse_mapping[current_code] = root.char
            return
        
        self.__make_codes_helper(root.left, current_code + "0")
        self.__make_codes_helper(root.right, current_code + "1")
    
    def __make_codes(self):
        root = heapq.heappop(self.__heap)
        current_code = ""
        self.__make_codes_helper(root, current_code)
    
    def __get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.__codes[char]
        return encoded_text
    
    def __get_padded_encoded_text(self, encoded_text):
        padded_amount = 8 - (len(encoded_text) % 8)
        for i in range(padded_amount):
            encoded_text += "0"
        
        padded_info = "{0:08b}".format(padded_amount)
        padded_encoded_text = padded_info + encoded_text
        return padded_encoded_text
    
    def __get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)
        
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]

            b.append(int(byte, 2))
        return b
    
    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        
        with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()
            
            frequency = self.__make_frequency_dict(text)
            self.__make_heap(frequency)
            self.__merge_nodes()
            self.__make_codes()
            
            encoded_text = self.__get_encoded_text(text)
            padded_encoded_text = self.__get_padded_encoded_text(encoded_text)
            
            b = self.__get_byte_array(padded_encoded_text)
            output.write(bytes(b))
        
        print("Compressed")
        return output_path
    
    def __remove_padding(self, text):
        padded_info = text[:8]
        extra_padding = int(padded_info, 2)
        
        text = text[8:] 
        text = text[:-1*extra_padding]
        return text
    
    def __decode_text(self, text):
        current_code = ""
        decoded_text = ""
        
        for bit in text:
            current_code += bit
            if current_code in self.__reverse_mapping:
                character = self.__reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
        
        return decoded_text
    
    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"
        
        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""
            byte = file.read(1)
            while len(byte) > 0:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
            
            text = self.__remove_padding(bit_string)
            decompressed_text = self.__decode_text(text)
            output.write(decompressed_text)
        
        print("Decompressed")
        return output_path
    
h = Huffman("large_text_file.txt")
output_path = h.compress()
print(output_path)

h.decompress(output_path)