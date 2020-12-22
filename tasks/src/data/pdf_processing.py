''' This code converts PDF files to .txt or .json files
    Credit: Juan Pablo Cuevas Gonzalez, Conrad Wilkinson Schwarz,
    Luis Zul, Ann Chia, Rubens Carvalho  '''
import os
import shutil
import io
import json

from io import StringIO
from io import BytesIO

import pdfminer
import pdfplumber

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

class PDFProcessing:
    listfiles = []
    def authorize_drive(self):
        '''
        Authorize this script to upload and download files to your computer.
        '''
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        driven = GoogleDrive(gauth)

        return driven

    def load_files(self, drive_client, source_id, temp_dir):
        '''
        drive_client: The client on which to call the list and download operations required.
        source id: The ID of the folder to download the files from.
        temp_dir: Temporary file directory to store preprocessing files. Will be deleted in clean_temp_folder
        '''
        print("loading files...")

        file_list = drive_client.ListFile(
            {'q':  "'%s' in parents" % source_id}).GetList()
        temp_path = temp_dir + "temp\\"
        os.makedirs(temp_path, exist_ok=True)
        output_file_list = []
        for f in file_list:
            print(f['title'])
            extension = f['title'].split(".")[1]
            if extension != "pdf": continue
            num = int(f['title'].split("_")[1].split(".")[0])
            if num > 10: continue
            # elif num > 300: continue
            fname = os.path.join(temp_path, f['title'])
            f_ = drive_client.CreateFile({'id': f['id']})
            f_.GetContentFile(fname)

            output_file_list.append(fname)

        return output_file_list, temp_path

    def upload_file(self, drive_client, destination_id, file):
        '''
        drive_client: The client on which to call the list and download operations required.
        destination_id: id of the upload drive folder. It's the string after the last '/'
        file: .txt file
        '''

        drive_file = drive_client.CreateFile(
            {'title': file.rsplit('\\')[-1], 'parents': [{'id': destination_id}]})
        print(destination_id,file.rsplit('\\')[-1])
        print(os.path.normpath(file))
        # drive_file.SetContentFile(file)
        drive_file.SetContentFile(os.path.normpath(file))
        drive_file.Upload()

    def clean_temp_folder(self, path):
        # Removes temporary file directory
        if os.path.isdir(path):
            shutil.rmtree(path)

    def pdf_to_txt(self, source_id, destination_id, temp_path):
        '''
        source_id: source id: The ID of the folder to download the files from.
        destination_id: id of the upload drive folder. It's the string after the last '/'
        temp_path: Temporary file directory. Will be deleted
        Demo input:
        from pdf_processing import PDF_Processing
        pf = PDF_Processing()
        pf.pdf_to_txt('1LmoiZ9IuwhMDIgyioG1xqorCnU1rEc7f',
              '1gvs5xzXsjIRR_YTqsj3luiejulJo8ryY',
              'C:\\Users\\FileDir\\Folder\\')
        '''

        # Authenticate with Google Drive and load files
        drive_client = self.authorize_drive()
        file_list, local_path = self.load_files(
            drive_client, source_id, temp_path)

        # Initial parameters
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, sio, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for file in file_list:
            file_name = file.rsplit('\\')[-1]
            print(file_name)
            print("opening document...")
            fp = open(file, "rb")

            print("document opened, start extracting")

            try:

              for page in PDFPage.get_pages(fp):
                print("extracted {} pages".format(page))
                interpreter.process_page(page)

            except:
              try:
                with pikepdf.Pdf.open(file) as pdf:
                  pdf.save(temp_path + 'output.pdf')

                fp = open(temp_path + 'output.pdf', "rb")

                for page in PDFPage.get_pages(fp):
                  print("extracted {} pages".format(page))
                  interpreter.process_page(page)

              except:
                print('-*-'*75)
                print('Please check this file:{}'.format(file))
                print('-*-'*75)
                self.listfiles.append(file)

            fp.close()
            text = sio.getvalue()
            text_file = file.rsplit('.')[0] + '.txt'
            f = io.open(text_file, 'w', encoding='utf-8')
            f.write(text)
            f.close()

            # Upload data as txt file
            self.upload_file(drive_client, destination_id, text_file)
            print("document uploaded")

        # Remove tmp folder
        self.clean_temp_folder(local_path)

        print('------------------------------------END----------------------------------------')

    def set_interpreter(self):
        #From https://stackoverflow.com/questions/38172601/separate-pdf-to-pages-using-pdfminer
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        laparams = LAParams()
        codec = 'utf-8'
        device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        return { 'sio': sio, 'device': device, 'interpreter': interpreter }

    def pdf_to_json_page_label(self, source_id, destination_id, temp_path):
        '''
        source_id: source id: The ID of the folder to download the files from.
        destination_id: id of the upload drive folder. It's the string after the last '/'
        temp_path: Temporary file directory. Will be deleted
        Demo input:
        from pdf_processing import PDF_Processing
        pf = PDF_Processing()
        pf.pdf_to_json_improved('1LmoiZ9IuwhMDIgyioG1xqorCnU1rEc7f',
              '1gvs5xzXsjIRR_YTqsj3luiejulJo8ryY',
              'C:\\Users\\FileDir\\Folder\\')
        '''

        # Authenticate with Google Drive and load files
        drive_client = self.authorize_drive()
        file_list, local_path = self.load_files(
            drive_client, source_id, temp_path)

        # Initial parameters
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, sio, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        for file in file_list:
            file_name = file.rsplit('\\')[-1]
            print(file_name)
            print("opening document...")
            fp = open(file, "rb")

            print("document opened, start extracting")

            # Create empty dict to store PDF doc data
            doc_data = dict()

            try:

                for page_num, page in enumerate(PDFPage.get_pages(fp)):
                    interpreter.process_page(page)
                    
                    text = sio.getvalue()
                    doc_data[f'page_{page_num + 1}'] = text
                    print("extracted {} pages".format(page))

                    init_params = self.set_interpreter()
                    sio = init_params["sio"]
                    interpreter = init_params["interpreter"]
                    device = init_params["device"]    


            except:
                try:
                    with pikepdf.Pdf.open(file) as pdf:
                        pdf.save(temp_path + 'output.pdf')

                    fp = open(temp_path + 'output.pdf', "rb")

                    for page_num, page in enumerate(PDFPage.get_pages(fp)):
                        print(page_num,page, "Estoy abajo")
                        
                        interpreter.process_page(page)
                        
                        text = sio.getvalue()
                        doc_data[f'page_{page_num + 1}'] = text

                        print("extracted {} pages".format(page))
                        # Initial parameters
                        init_params = self.set_interpreter()
                        sio = init_params["sio"]
                        interpreter = init_params["interpreter"]
                        device = init_params["device"]
                except:
                    print('-*-'*75)
                    print('Please check this file:{}'.format(file))
                    print('-*-'*75)
                    self.listfiles.append(file)

            fp.close()
            text_file = file.rsplit('.')[0] + '.json'
            with open(text_file, 'w') as fout:
                json.dump(doc_data, fout)
            fout.close()

            # Upload data as txt file
            self.upload_file(drive_client, destination_id, text_file)
            print("document uploaded")

        # Remove tmp folder
        self.clean_temp_folder(local_path)

        print('------------------------------------END----------------------------------------')    

    # def pdf_to_json_update(self, source_id, destination_id, temp_path, source_json):
    def pdf_to_json_update(self, destination_id, temp_path, source_json):
        '''
        source_id: source id: The ID of the folder to download the files from.
        destination_id: id of the upload drive folder. It's the string after the last '/'
        temp_path: Temporary file directory. Will be deleted
        source_json: Location of the processed json that the app is reading (by country).
        Demo input:
        from pdf_processing import PDF_Processing
        pf = PDF_Processing()
        pf.pdf_to_json('1LmoiZ9IuwhMDIgyioG1xqorCnU1rEc7f',
              '1gvs5xzXsjIRR_YTqsj3luiejulJo8ryY',
              'C:\\Users\\FileDir\\Folder\\')
        '''        
        source_json = str(source_json).lower().strip()
        json_path = os.path.join(r"C:\Users\dcalle.MATONE\Documents\GitHub\wrilatinamerica\data\processed\2020-10-04", source_json.title(), "json_improved")
        json_list = [file_name.split(".")[0] for file_name in os.listdir(json_path)]

        token = {"chile": "1zeMzuIPoupf5ZOltdYgYQDiL1IO0LZLQ", 
                "mexico": "1HdvZyC4-5HrPikE4jWfQ5tT9r_n0QATo",
                "el salvador": "16wfnPUZ6PU-Vv6_QqMQLV7KmyyGl2oPs",
                "guatemala": "1rNU5eqMmVr1RtZoC-dyKiLd8O-m_EXdE",
                "peru": "1efXPrueAsUawrnjQNPaTKWz9gHx2vDT9"}

        try:
            source_id = token[source_json]
        except:
            print("Invalid country")

        print("loading files...")

        # Authenticate with Google Drive and load files
        drive_client = self.authorize_drive()
        
        file_list = drive_client.ListFile(
            {'q':  "'%s' in parents" % source_id}).GetList()

        # orig_list = [file_name['title'].split(".")[0] for file_name['title'] in file_list]

        missing_list = [f for f in file_list if f['title'].split('.')[0] not in json_list]
        # missing_list = list(set(orig_list).difference(json_list))

        temp_path = temp_path + "temp\\"
        os.makedirs(temp_path, exist_ok=True)
        output_file_list = []
        for f in missing_list:
            print(f['title'])
            extension = f['title'].split(".")[1]
            if extension != "pdf": continue
            
            fname = os.path.join(temp_path, f['title'])
            f_ = drive_client.CreateFile({'id': f['id']})
            f_.GetContentFile(fname)

            output_file_list.append(fname)

        file_list = output_file_list
        local_path = temp_path

        # Initial parameters
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, sio, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        for file in file_list:
            file_name = file.rsplit('\\')[-1]
            print(file_name)
            print("opening document...")
            fp = open(file, "rb")

            print("document opened, start extracting")

            # Create empty dict to store PDF doc data
            doc_data = dict()

            try:

                for page_num, page in enumerate(PDFPage.get_pages(fp)):
                    interpreter.process_page(page)
                    
                    text = sio.getvalue()
                    doc_data[f'page_{page_num + 1}'] = text
                    print("extracted {} pages".format(page))

                    init_params = self.set_interpreter()
                    sio = init_params["sio"]
                    interpreter = init_params["interpreter"]
                    device = init_params["device"]    


            except:
                try:
                    with pikepdf.Pdf.open(file) as pdf:
                        pdf.save(temp_path + 'output.pdf')

                    fp = open(temp_path + 'output.pdf', "rb")

                    for page_num, page in enumerate(PDFPage.get_pages(fp)):
                        print(page_num,page, "Estoy abajo")
                        
                        interpreter.process_page(page)
                        
                        text = sio.getvalue()
                        doc_data[f'page_{page_num + 1}'] = text

                        print("extracted {} pages".format(page))
                        # Initial parameters
                        init_params = self.set_interpreter()
                        sio = init_params["sio"]
                        interpreter = init_params["interpreter"]
                        device = init_params["device"]
                except:
                    print('-*-'*75)
                    print('Please check this file:{}'.format(file))
                    print('-*-'*75)
                    self.listfiles.append(file)

            fp.close()
            text_file = file.rsplit('.')[0] + '.json'
            with open(text_file, 'w') as fout:
                json.dump(doc_data, fout)
            fout.close()

            # Upload data as txt file
            self.upload_file(drive_client, destination_id, text_file)
            print("document uploaded")

        # Remove tmp folder
        self.clean_temp_folder(local_path)

        print('------------------------------------END----------------------------------------')    

    def pdf_to_json(self, source_id, destination_id, temp_path):
        '''
        source_id: source id: The ID of the folder to download the files from.
        destination_id: id of the upload drive folder. It's the string after the last '/'
        temp_path: Temporary file directory. Will be deleted
        Demo input:
        from pdf_processing import PDF_Processing
        pf = PDF_Processing()
        pf.pdf_to_json('1LmoiZ9IuwhMDIgyioG1xqorCnU1rEc7f',
              '1gvs5xzXsjIRR_YTqsj3luiejulJo8ryY',
              'C:\\Users\\FileDir\\Folder\\')
        '''
        # Authenticate with Google Drive and load files
        drive_client = self.authorize_drive()
        file_list, local_path = self.load_files(
            drive_client, source_id, temp_path)

        for file in file_list:
            file_name = file.rsplit('\\')[-1]
            print(file_name)
            print("opening document...")

            # Open pdf
            with pdfplumber.open(file) as pdf:

                print("document opened, start extracting")

                # Create empty dict to store PDF doc data
                doc_data = dict()

                # Extract document metadata, store in doc data
                metadata = pdf.metadata
                doc_data['metadata'] = metadata

                # Create empty list to store page data
                data_per_page = []

                # Extract page data
                doc = pdf.pages
                for page in doc:

                    print("extracted {} pages".format(page))

                    # Store page data as dict
                    page_data = dict()
                    page_data['page_id'] = page.page_number
                    page_data['full_text'] = page.extract_text()
                    #page_data['annotations'] = page.annots
                    #page_data['links'] = page.hyperlinks
                    data_per_page.append(page_data)

                doc_data['data_per_page'] = data_per_page

                # Create JSON object of combined document data
                output_file = file.rsplit('.')[0] + '.json'
                with open(output_file, 'w') as fout:
                    json.dump(doc_data, fout)
                fout.close()

            # Upload data as JSON file
            self.upload_file(drive_client, destination_id, output_file)
            print("document uploaded")

        # Remove tmp folder
        self.clean_temp_folder(local_path)

        print('------------------------------------END----------------------------------------')
