import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

NODE_PATH = os.getenv('NODE_PATH')
NUM_BEADS = int(os.getenv('NUM_BEADS'))

def pin(read_path="./beads", save_path="./data"):
    def pin_img_to_pinata(img_path):
        ipfs_hash = subprocess.check_output([NODE_PATH,'./_pinImgToPinata.js', img_path])
        return ipfs_hash.decode().strip()

    def pin_metadata_to_pinata(metadata, img_ipfs_hash, number):
        metadata['attributes'].append({'display_type': 'number', 'trait_type': 'Edition', 'max_value': 1, 'value': 1})
        metadata['name'] = f'RGBead #{number} of {NUM_BEADS}'
        metadata['image'] = "https://gateway.pinata.cloud/ipfs/" + img_ipfs_hash
        metadata_ipfs_hash = subprocess.check_output([NODE_PATH, './_pinMetadataToPinata.js', json.dumps(metadata), "1"])
        return metadata_ipfs_hash.decode().strip()        

    mhashes = []

    for i in range(10):
        impath = os.path.join(read_path, str(i), f"{i}.png")
        imhash = pin_img_to_pinata(impath)
        m = json.load(open(os.path.join(read_path, str(i), f"{i}.json")))
        mhash = pin_metadata_to_pinata(m, imhash, str(i+1))
        mhashes.append(mhash)
        url = f"https://gateway.pinata.cloud/ipfs/{mhash}"
        print(url)

    json.dump(mhashes, open(os.path.join(save_path, "metadata_hashes.json"), "w"))

pin()