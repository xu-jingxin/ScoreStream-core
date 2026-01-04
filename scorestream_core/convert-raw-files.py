from music21 import converter, stream
import subprocess
from timeit import default_timer as timer
from datetime import timedelta

# from basic_pitch.inference import predict_and_save


input_pdf_filepath = "Polonaise.pdf"
input_audio_filepath = r"C:\Users\jingx\git_wa\ScoreStream-core\scorestream_core\files\Moonlight_Sonata_1_1st_page.m4a"


def call_audiveris(sheet_path):
    start = timer()

    result = subprocess.run(
        [
            "C:/Program Files/Audiveris/bin/Audiveris.bat",
            "-export",
            "-batch",
            "-output",
            "C:/Users/jingx/git_wa/ScoreStream-core/scorestream_core",
            sheet_path,
        ],
        # capture_output=True,
        # text=True,
    )

    end = timer()
    print(timedelta(seconds=end - start))  # this times how long Audiveris takes


strips_paths = ["page_1_strip_2.png", "page_1_strip_3.png"]

for strip in strips_paths:
    call_audiveris(strip)

call_audiveris()
# predict_and_save(
#     input_audio_filepath,
#     r'C:\Users\jingx\git_wa\ScoreStream-core\scorestream_core',
#     save-midi=True,
#     True,
#     <save-model-outputs>,
#     <save-notes>,
#     <model-path>
# )
