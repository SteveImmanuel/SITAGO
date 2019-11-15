import face_recognition
import numpy as np
import os
import sys
from dataclasses import dataclass
from typing import List

FACE_DIRECTORY = 'face'


@dataclass()
class FaceData():
    face_features: List[np.array]
    face_names: List[str]


def loadFace():
    file_list = os.listdir(FACE_DIRECTORY)

    face_file_list = [f for f in file_list if f.endswith('.face')]

    face_data_list = [
        np.load(os.path.join(FACE_DIRECTORY, filename)) for filename in face_file_list
    ]
    face_name_list = [filename[:-5] for filename in face_file_list]

    return FaceData(face_data_list, face_name_list)


def createFaceData(image_path: str, name: str):
    picture = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(picture)[0]

    npy_dir = os.path.join(FACE_DIRECTORY, '{}.npy'.format(name))
    face_dir = os.path.join(FACE_DIRECTORY, '{}.face'.format(name))

    np.save(npy_dir, face_encoding)

    os.rename(npy_dir, face_dir)


def testFace(image_path: str):
    face_features = []
    face_names = []

    # Load face data
    if os.path.isdir(FACE_DIRECTORY):
        face_data = loadFace()
        face_features = face_data.face_features
        face_names = face_data.face_names
    else:
        raise Exception('No face data found')

    test_picture = face_recognition.load_image_file(image_path)
    test_feature = face_recognition.face_encodings(test_picture)[0]

    result_list = face_recognition.compare_faces(face_features, test_feature)

    result_face_index = [i for i, result in enumerate(result_list) if result]

    if len(result_face_index) >= 1:
        return face_names[result_face_index[0]]
    else:
        return None


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise Exception('Usage: python face.py <image to test>')

        if sys.argv[1] == 'enroll':
            if len(sys.argv) < 4:
                raise Exception('Usage: python face.py enroll <image> <name>')
            else:
                createFaceData(sys.argv[2], sys.argv[3])
        else:
            file_test = sys.argv[1]
            if os.path.isfile(file_test):
                print("Found : {}".format(testFace(file_test)))
            else:
                raise Exception('Test file not found')
    except Exception as err:
        print("Err: {}".format(err))