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


class faceParser():
    def __init__(self, *args):
        if len(args) == 1:
            self.loadFace(args[0])
        else:
            self.loadFace(FACE_DIRECTORY)

    def loadFace(self, face_directory: str) -> None:
        file_list = os.listdir(face_directory)

        face_file_list = [f for f in file_list if f.endswith('.face')]

        face_data_list = [
            np.load(os.path.join(FACE_DIRECTORY, filename)) for filename in face_file_list
        ]
        face_name_list = [filename[:-5] for filename in face_file_list]

        self.face_data = FaceData(face_data_list, face_name_list)

    def createFaceData(self, image_path: str, name: str) -> None:
        picture = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(picture)[0]

        npy_dir = os.path.join(FACE_DIRECTORY, '{}.npy'.format(name))
        face_dir = os.path.join(FACE_DIRECTORY, '{}.face'.format(name))

        np.save(npy_dir, face_encoding)

        os.rename(npy_dir, face_dir)

    def testFace(self, image_path: str) -> str:
        face_features = self.face_data.face_features
        face_names = self.face_data.face_names

        test_picture = face_recognition.load_image_file(image_path)
        test_feature = face_recognition.face_encodings(test_picture)

        if len(face_recognition.face_encodings(test_picture)) < 1:
            raise Exception('No face detected')

        test_feature = test_feature[0]

        result_list = face_recognition.compare_faces(face_features, test_feature, tolerance=0.4)

        result_face_index = [i for i, result in enumerate(result_list) if result]

        if len(result_face_index) >= 1:
            return face_names[result_face_index[0]]
        else:
            return None


if __name__ == '__main__':
    try:
        parser = faceParser()

        if len(sys.argv) < 2:
            raise Exception('Usage: python face.py <image to test>')

        if sys.argv[1] == 'enroll':
            if len(sys.argv) < 4:
                raise Exception('Usage: python face.py enroll <image> <name>')
            else:
                parser.createFaceData(sys.argv[2], sys.argv[3])
        else:
            file_test = sys.argv[1]
            if os.path.isfile(file_test):
                print("Found : {}".format(parser.testFace(file_test)))
            else:
                raise Exception('Test file not found')
    except Exception as err:
        print("Err: {}".format(err))