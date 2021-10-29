from flask import Flask, request, jsonify
from google.cloud import storage
import os
import subprocess
storage_client = storage.Client()
bucket_origem = storage_client.get_bucket("catalobyte-convert")
bucket_destino = storage_client.get_bucket("catalobyte-pre-speech")

app = Flask(__name__)

@app.route("/", methods=["POST"])
def receive():
    data = request.get_json()
    gs_uri = data['filepath'] #name: '1sPcgixNZobTGi1McrKK7UyaZUd2/o6h0z2g9c7-1635332818807-8833777097.avi

    full_path_uri = gs_uri.split('/')
    uid_firebase = full_path_uri[0] # 1sPcgixNZobTGi1McrKK7UyaZUd2

    splifile = full_path_uri[1].split('-') # o6h0z2g9c7-1635332818807-8833777097.avi
    spliexten = full_path_uri[1].split('.') # o6h0z2g9c7-1635332818807-8833777097.avi
    extension = spliexten[1] # avi
    indexmanti = splifile[0] # o6h0z2g9c7
    timestampname = splifile[1] # 1635332818807
    nomearquivo = splifile[2] # 8833777097.avi
    onlyname = nomearquivo.split('.')[0] # 8833777097

    tempfile = "temp."+extension
    destname = timestampname+".flac"

    # gs://catalobyte-convert/1sPcgixNZobTGi1McrKK7UyaZUd2/o6h0z2g9c7-1635332818807-8833777097.avi
    if not os.path.exists(tempfile):
        os.mknod(tempfile)
    with open(tempfile, 'wb+') as file_obj:
        storage_client.download_blob_to_file('gs://catalobyte-convert/'+gs_uri, file_obj)

    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', tempfile, '-f', 'flac','-ac', '1', '-ab', '192000', '-ar', '16000', '-vn', destname]
    subprocess.call(cmd)

    blob = bucket_destino.blob(uid_firebase+'/'+indexmanti+'/'+onlyname+'/'+destname)
    blob.upload_from_filename(destname)
    blob_del = bucket_origem.delete_blob(gs_uri)

    return "ok"

if __name__ == "__main__":
    # Used when running locally only. When deploying to Cloud Run,
    # a webserver process such as Gunicorn will serve the app.
    app.run(host="localhost", port=8080, debug=True)
