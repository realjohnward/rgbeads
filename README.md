

<h2><b>Requirements</b></h2>
<ul>
<li>Python 3.8 or higher (lower versions might work but they're untested)</li>
<li>Node JS 12.22.1 or higher (lower versions might work but they're untested)</li>
</ul>
<h2><b>Setup</b></h2>
<ul>
<li>Run these commands to clone the repository and enter the home directory:<br/><code>git clone https://github.com/realjohnward/rgbeads.git && cd rgbeads</code></li> 
<li>Run this script to install the required packages:<br/><code>pip install -r requirements.txt</code></li>
</ul>

<h2><b>Application</b></h2>
<h3><b>Step 1: Deploy ERC-721 Contract</b></h3>
<ul>
<li>Compile contract in remix and save the bytecode and ABI locally.</li>
<li>Set environment variables</li>
<li>Deploy contract by running the following script:<br/><code>python deploy.py</code></li>
<li>Read transaction receipt to get the contract address and set it to the CONTRACT_ADDRESS environment variable.</li>
</ul>

<h3><b>Step 2: Generate Images and Metadata Blobs</b></h3>
<ul>
<li>Generate 10K images and blobs for the beads by running the following script:<br/><code>python generate.py</code></li>
</ul>

<h3><b>Step 3: Pin Images and Blobs to IPFS</b></h3>
<ul>
<li>Run this script:<br/><code>python pin.py</code></li>
</ul>

<h3><b>Step 4: Mint IPFS hashes to smart contract to create the NFTs.</b></h3>
<ul>
<li>Run this script:<br/><code>python mint.py</code></li>
<li>View NFTs by opening this url in your browser: https://testnets.opensea.io/collection/{INSERT CONTRACT ADDRESS HERE}</li>
</ul>