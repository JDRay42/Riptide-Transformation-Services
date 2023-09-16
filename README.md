# Riptide Transformation Services

**Note:** This is my first foray into creating an open source project.  What you see below in this README is, in all honesty, the output derived from asking ChatGPT a bunch of questions about how to setup an open source project on GitHub.  I don't necessarily trust that it got things right.  I will appreciate help making this project better, but don't need anyone flinging poo at me or anyone else contributing here.

**Riptide Transformation Services** is a collection of text transformation utilities designed as an accessory to the broader Riptide suite of document transformation and inquiry applications. While these services are created as part of the Riptide suite, they can stand alone and might be beneficial to a broader audience.

## Features

### 1. **NER Tagging**
- **Endpoint**: `/ner/`
- Extract named entities from the provided text.

### 2. **Text Vectorization**
- **Endpoint**: `/text2vec/`
- Convert the provided text into a numerical vector representation.

### 3. **Text Paraphrasing**
- **Endpoint**: `/paraphrase/`
  - Returns a single paraphrased version of the input text.
- **Endpoint**: `/paraphrase/multi/`
  - Returns an array of paraphrased options for the user to select.

### 4. **Documentation**
- **Endpoint**: `/docs/`
- FastAPI automatically provides an interactive API documentation interface to explore and test the available endpoints.

### 5. **User Interface**
- **Endpoint**: `/`
- Styling straight out of 1995.  It sure would be nice if someone with skills in CSS would come along and fix this.
- A user-friendly interface with tabbed pages for each transformation service, allowing easy access and usage.

## Authentication

To access the transformation endpoints, an API key is required. Include the API key in the header of your request using the `Authorization` key.

## Usage

To use any of the services, send a `POST` request to the respective endpoint with the appropriate payload. Detailed API documentation and payload structures can be found at the `/docs/` endpoint.

## Contributing

If you're interested in contributing to the Riptide Transformation Services, please check out our contributing guidelines (below) and feel free to submit a pull request!

## License

This project is licensed under the `BSD 3-Clause License`. See the `LICENSE` file for details.

# Getting Started

## Generating SSL Keys

The app runs over https, which requires SSL.  You'll need to generate a private key and a self-signed certificate. Follow the steps below to create these SSL keys:

### 1. Generate a Private Key

To generate a private key (`key.pem`), run the following command:

\```bash
openssl genpkey -algorithm RSA -out key.pem
\```

### 2. Create a Self-Signed Certificate

After you've generated a private key, create a self-signed certificate (`cert.pem`) using the command below:

\```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
\```

This command will prompt you for additional information such as your country, state, etc. Fill them out as needed.

### 3. Using the SSL Keys with the App

Once you have both `key.pem` and `cert.pem`, ensure they're in a secure location and update the app's `.env` file to use them for SSL:

\```plaintext
SSL_CERT_PATH=/path/to/your/cert.pem
SSL_KEY_PATH=/path/to/your/key.pem
\```

### Note

- This guide creates a self-signed certificate which is great for development and testing. For production environments, consider obtaining a certificate from a trusted certificate authority (CA).
- Self-signed certificates can cause browser warnings because they're not issued by a trusted CA. Ensure you understand these implications before deploying in a user-facing environment.

## Setting Up Your Environment (Python)

1. Fork the repository on GitHub.
2. Clone your fork to your local machine: 
   ```
    git clone https://github.com/JDRay42/Riptide-Transformation-Services.git
   ```
3. Set up a virtual environment (optional but recommended): 
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. **Set Up Environment Variables**:
    - Copy the `example.env` to `.env`:
        ```bash
        cp example.env .env
        ```
    - Edit the `.env` file to suit your needs using your favorite text editor. Ensure you set all necessary variables.
    - Be sure to update the paths to the SSL certificates.
    
5. Install the required packages: 
   ```
   pip install -r requirements.txt
   ./launch.sh
   ```
## Setting Up Your Environment (Docker)

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/JDRay42/Riptide-Transformation-Services.git
    cd Riptide-Transformation-Services
    ```

2. **Set Up Environment Variables**:
    - Copy the `example.env` to `.env`:
        ```bash
        cp example.env .env
        ```
    - Edit the `.env` file to suit your needs using your favorite text editor. Ensure you set all necessary variables.
    - Be sure to update the paths to the SSL certificates.
    
3. **Run with Docker Compose**:
    Ensure Docker and Docker Compose are installed. Then, initiate the services with:
    ```bash
    docker-compose up --build
    ```

## Usage
   If you just used the default .env file by copying its contents from example.env, then all you'll need to do is open a web browser and to to:
   `https://localhost:8019`

   Otherwise, based on your configuration, open `https://{$HOST}:{$PORT}`

   **Note:** The default word limit is 400 words of text entry.  This enables a certain degree of decent performance while respecting BERT's 512-token limit.  In places where BERT divides certain words into multiple tokens, 400 seemed like a good line to draw in the sand.  If you want faster performance, lower the value in the `.env` file and restart the server.  If you want larger context capability (more than 512 tokens), change the model using the settings in the section at the bottom of the `.env`.
   
# Contributing to Riptide Transformation Services

First and foremost, thank you for considering contributing to Riptide Transformation Services! We value all contributions, whether you're fixing a typo, suggesting improvements, or proposing a new feature.

## Making Changes

1. Create a new branch for your feature or bugfix: 
   ```
   git checkout -b your-branch-name
   ```
2. Make your changes.
3. Write tests that cover your changes (if applicable).
4. Ensure all tests pass.
5. Commit your changes: 
   ```
   git commit -m "Your detailed commit message"
   ```
6. Push your changes to your fork on GitHub.

## Submitting a Pull Request

1. Go to the [Riptide Transformation Services repository](https://github.com/JDRay42/Riptide-Transformation-Services) on GitHub.
2. Click the "New Pull Request" button.
3. Select your fork and the branch you created.
4. Submit your pull request with a brief description of your changes.

## Code Review

1. Once your pull request is submitted, maintainers will review your code.
2. Address any feedback or changes requested by the maintainers.
3. Once approved, your changes will be merged into the main branch.

## Code of Conduct

### Purpose

The main goal of the Riptide Transformation Services is to be inclusive to the largest number of contributors, with the most varied and diverse backgrounds possible. As such, we are committed to providing a friendly, safe, and welcoming environment for all, regardless of gender, sexual orientation, ability, ethnicity, socioeconomic status, and religion (or lack thereof).

This Code of Conduct outlines our expectations for all those who participate in our community, as well as the consequences for unacceptable behavior.

### Open Source Citizenship

A supplemental goal of this Code of Conduct is to increase open-source citizenship by encouraging participants to recognize and strengthen the relationships between our actions and their effects on our community.

### Expected Behavior

* Participate in an authentic and active way.
* Exercise consideration and respect in your speech and actions.
* Attempt collaboration before conflict.
* Refrain from demeaning, discriminatory, or harassing behavior and speech.
* Be mindful of your surroundings and of your fellow participants.

### Unacceptable Behavior

Unacceptable behaviors include:

* Harassment, including offensive verbal comments related to gender, sexual orientation, race, religion, disability, etc.
* Trolling, insulting/derogatory comments, and personal or political attacks.
* Publishing others' private information, such as a physical or electronic address, without explicit permission.
* Other conduct which could reasonably be considered inappropriate in a professional setting.

### Consequences of Unacceptable Behavior

Unacceptable behavior from any community member will not be tolerated. Anyone asked to stop unacceptable behavior is expected to comply immediately.

If a community member engages in unacceptable behavior, the project maintainers may take any action they deem appropriate, up to and including a temporary ban or permanent expulsion from the community without warning.

### Reporting Guidelines

If you are subject to or witness unacceptable behavior, or have any other concerns, please notify a project maintainer as soon as possible.

### Addressing Grievances

Only permanent resolutions (such as bans) may be appealed. To appeal a decision of the working group, contact a project maintainer with your appeal and the maintainers will review the decision.

### Scope

This Code of Conduct applies both within project spaces and in public spaces when an individual is representing the project or its community.

### Contact Info

For any concerns or to report violations, please contact riptide.project.19@gmail.com.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 1.4, available at https://www.contributor-covenant.org/version/1/4/code-of-conduct.html
