from django.shortcuts import render, redirect
import yt_dlp
import re
from django.http import HttpResponse, HttpResponseRedirect
import yt_dlp

#Home Page View
def home(request):
    error_message = ''
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        if not video_url:
            error_message = 'Please enter a YouTube video URL.'
        elif not re.match(r'(https?://)?(www\.)?(youtube|m.youtube|youtu|youtube-nocookie)\.(com|be)/.+', video_url):
            error_message = 'Please enter a valid YouTube URL.'
        else:
            request.session['video_url'] = video_url  # Store the video URL in session
            return redirect('download')
    return render(request, 'downloader/home.html', {'error_message': error_message})

def download(request):
    video_url = request.session.get('video_url')
    if video_url:
        try:
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'restrictfilenames': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_info = {
                    'title': info_dict.get('title', None),
                    'thumbnail': info_dict.get('thumbnail', None),
                    'formats': [
                        {
                            'format_id': f.get('format_id'),
                            'format': f.get('format'),
                            'ext': f.get('ext'),
                            'filesize': round(f.get('filesize', 0) / 1048576, 2) if f.get('filesize') else 'N/A',
                            'url': f.get('url'),
                        }
                        for f in info_dict.get('formats', [])
                        if f.get('height') is not None and f['height'] >= 360 and f.get('acodec') != 'none' and f.get('filesize')
                    ]
                }
                request.session['video_info'] = video_info  # Store video info in session
                return render(request, 'downloader/download.html', {'video_info': video_info})

        except Exception as e:
            return HttpResponse(f"Error fetching video details: {e}")
    return HttpResponse("No video URL provided.")