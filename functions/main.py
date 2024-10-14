import io
import pathlib
from PIL import Image
from firebase_admin import initialize_app
initialize_app()
from firebase_admin import storage, firestore
from firebase_functions import storage_fn
import google.generativeai as genai
from firebase_functions.params import SecretParam
import json


api_key_firebase = SecretParam('GOOGLE_GENAI_API_KEY')
genai.configure(api_key=api_key_firebase.value)
prompt = """give me question answers. The questions should be free response not multiple choice. The answers should be detailed and informative. \n
Format: \n
[
  {
  "QA_Pairs": [
    {
      "question": "What is the capital of France?",
      "answer": "Paris"
    },
    {
      "question": "Who painted the Mona Lisa?",
      "answer": "Leonardo da Vinci"
    }
  ]
}
]
Remember, do not use any of the formatting on the website/image. Make the questions as if the person answering them didn't have access to the image or website.
"""

# Using `response_schema` requires one of the Gemini 1.5 Pro models
model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"response_mime_type": "application/json"})

def save_question_answer_firestore(questions_answer):
    db = firestore.client()
    doc_ref = db.collection(u'Question_Answer_From_Bucket').document()
    doc_ref.set(questions_answer)
    

@storage_fn.on_object_finalized()
def get_QA_from_image(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]):
    """When the image is uploaded, extract the QA from the image."""
    bucket_name = event.data.bucket
    file_path = pathlib.PurePath(event.data.name)
    content_type = event.data.contentType
    
    #File must go to image folder
    if not content_type or not content_type.startswith("image/"):
        print(f"This is not an image. ({content_type})")
        return

    bucket = storage.bucket(bucket_name)
    
    image_blob = bucket.blob(str(file_path))
    image_bytes = image_blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_bytes))
    
    response = model.generate_content([prompt, image])
    loaded_json = json.loads(response.text)
    QA = json.dumps(loaded_json)
    QA = json.loads(QA)
    
    
    # add image path to QA
    QA = json.loads(QA)
    QA['image_path'] = f"gs://{bucket_name}/{file_path}"
    
    # uploads to firestore in proper format to be used in a VM to train.
    save_question_answer_firestore(QA)
    