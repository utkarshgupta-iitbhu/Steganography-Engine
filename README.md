# Advanced Steganography Engine 🕵️‍♂️🔒

>An asynchronous, multi-threaded desktop application that securely conceals files and text within the spatial domain of lossless images.

Unlike basic steganography scripts that simply write plaintext into pixels, this engine acts as a secure data vault. It bridges **industry standard cryptography** with **digital steganography** to ensure that even if the presence of hidden data is detected, the payload remains computationally impossible to breach.

---

## 🚀 Demo

To run the application without setting up a local development environment, you can download the pre-compiled executable:

[Download from Google Drive](https://drive.google.com/file/d/1mkTKnbbDFTyMxOEcLktejl8IdUsAZtbY/view?usp=drive_link)

---

## Why This Project Exists

Traditional encryption protects data, but encrypted files themselves attract attention.

For example:

* A `.zip` protected by AES clearly indicates that sensitive information exists.
* An encrypted document immediately tells an attacker something valuable is being protected.

This project solves that problem by:

* Encrypting the data first.
* Concealing the encrypted output inside an innocent-looking image.

The resulting image appears completely normal while secretly containing the protected payload.

---

## 🛡️ Security Architecture & Countermeasures

This engine implements a multi-layered security model to protect the payload against brute-force attacks, sequential extraction, and file tampering.


### 1. AES-256-GCM Authenticated Encryption

The project uses:

```python
cryptography.hazmat.primitives.ciphers.aead.AESGCM
```

AES-GCM provides:

#### Confidentiality
Only the correct password can decrypt the hidden message.

#### Integrity
Any modification to the encrypted payload is detected.

#### Authentication
Attackers cannot forge valid ciphertext.

---

### 2. PBKDF2 Key Stretching

Human passwords are weak.

Instead of directly using a password as the encryption key, the system derives a strong 256-bit key using:

* PBKDF2
* SHA-256
* 480,000 iterations

This greatly increases resistance against:

* Dictionary attacks
* Brute-force attacks
* Rainbow tables

---

### 3. Unique Random Salt

Every encryption generates:

```python
salt = os.urandom(16)
```

Benefits:

* Same password never produces the same key.
* Prevents precomputed rainbow-table attacks.
* Ensures uniqueness across encryptions.

---

### 4. Random Nonce Generation

AES-GCM requires a nonce:

```python
nonce = os.urandom(12)
```

Purpose:

* Guarantees fresh encryption every time.
* Prevents ciphertext reuse vulnerabilities.

---

### 5. Password-Based Pixel Randomization

Instead of hiding data sequentially, pixels are shuffled:

```python
random.Random(seed).shuffle(pixel_map)
```

Advantages:

* Eliminates predictable embedding patterns.
* Makes statistical steganalysis significantly harder.
* Requires knowledge of the password to locate payload bits.

---

### 6. Authentication Tag Verification

AES-GCM automatically creates an authentication tag.

If:

* a wrong password is used, or
* even one hidden bit changes,

then:

```python
InvalidTag
```

is raised and decryption fails.

This prevents:

* Silent corruption
* Data forgery
* Manipulation attacks

---

### 7. Payload Validation

Before decoding, the engine verifies that the payload contains:

```
Salt
Nonce
Authentication Tag
```

Malformed or incomplete data is rejected immediately.

This protects against:

* Corrupted images
* Invalid payloads
* Random data interpretation

---

### 8. Capacity Checking

The encoder calculates:

```python
Maximum Capacity
=
(width × height × 3 − 32)/8
```

If the payload exceeds image capacity:

* Encoding is aborted.
* No partial corruption occurs.

---

### 9. Lossless PNG Enforcement

Output images are always saved as:

```python
PNG
```

because PNG uses lossless compression.

Lossy formats such as:

* JPEG
* WEBP (lossy)

would destroy hidden bits.

---

### 10. Thread-Safe Operations

Long-running encryption and extraction are executed in separate threads.

Benefits:

* GUI remains responsive.
* Prevents freezing.
* Improves user experience.

---

### 11. Deep Scan Forensic Mode

The engine includes a low-level analysis mode that:

* Reads every LSB from every pixel.
* Produces raw binary dumps.
* Optionally filters human-readable strings.

Useful for:

* Digital forensics.
* Steganography research.
* Payload recovery experiments.

---
---

## ⚙️ Features

### 🔒 AES-256 Encryption

* Industry-standard AES-GCM authenticated encryption.
* Ensures confidentiality and integrity.

### 🖼 Image Steganography

* Hides data inside RGB pixels using Least Significant Bit (LSB) manipulation.

### 📁 Hide Files or Text

Supports:

* Text messages
* Documents
* Images
* Executables
* Any binary file

### 🔑 Password-Based Protection

* User password is transformed into a secure cryptographic key using PBKDF2.

### 🎲 Randomized Embedding

* Pixel positions are shuffled using a password-derived seed.
* Prevents predictable hiding patterns.

### 🛡 Tamper Detection

* Any modification to the hidden ciphertext causes decryption failure.

### 🔍 Deep Scan Mode

Forensic mode capable of:

* Dumping all LSB bits.
* Recovering raw hidden information.
* Searching for readable strings.

---

## 🏗️ Software Architecture

The codebase adheres strictly to modular design principles, isolating the UI from the mathematics:

* `main.py`: The asynchronous UI coordinator, state manager, and threading controller.
* `crypto_engine.py`: A standalone cryptographic vault utilizing the `cryptography` library.
* `stego_engine.py`: The pixel manipulation and spatial grid coordinator using `Pillow`.

---

## 🚀 Installation & Usage

### Prerequisites

* Python 3.8+
* Minimum required libraries:
```bash
pip install customtkinter cryptography Pillow

```

### Running the Engine

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Advanced-Steganography-Engine.git

```


2. Navigate to the directory:
```bash
cd Advanced-Steganography-Engine

```


3. Execute the application:
```bash
python main.py

```
---

## Data Format

The hidden payload structure is:

```
┌─────────┬─────────┬─────────────┐
│  Salt   │ Nonce   │ Ciphertext  │
│ 16 Bytes│12 Bytes │ AES-GCM     │
└─────────┴─────────┴─────────────┘
```

Before embedding, a 32-bit header containing payload size is added:

```
[Length Header][Encrypted Payload]
```

---

## Important Delivery Note

Steganography relies on **lossless** pixel data. If you encode an image and send it via platforms that heavily compress media (e.g., WhatsApp, Discord, Instagram), the AES payload will be permanently destroyed. Always transfer the resulting `.png` files via secure cloud links (Google Drive, Dropbox), email attachments, or physical USB drives.

---

## 👨‍💻 Author

Developed by **Utkarsh Gupta**
