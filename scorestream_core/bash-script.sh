
# might as well call the audiveris from here

# first chop the pdfs
python3 chop_pdf.py

# figure out how to iterate ltr
ffmpeg -loop 1 -t 3.5 -i page_1_strip_2.png \
-loop 1 -t 3.7 -i page_1_strip_3.png \
-loop 1 -t 2.8 -i page_1_strip_4.png \
-i audio.mp3 \
-filter_complex "
[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]
" \
-map "[v]" -map 3:a \
-r 30 -pix_fmt yuv420p -shortest final.mp4
