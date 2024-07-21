import os
import torch
from num2words import num2words
import io
import soundfile as sf


def translit2rus(text):
    translit_map = {
        'a': 'а', 'b': 'б', 'c': 'ц', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х',
        'i': 'и', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
        'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс',
        'y': 'ы', 'z': 'з',
        'A': 'А', 'B': 'Б', 'C': 'Ц', 'D': 'Д', 'E': 'Е', 'F': 'Ф', 'G': 'Г', 'H': 'Х',
        'I': 'И', 'J': 'Й', 'K': 'К', 'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П',
        'Q': 'К', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У', 'V': 'В', 'W': 'В', 'X': 'Кс',
        'Y': 'Ы', 'Z': 'З',
        '/': ' дробь ',
        '0': ' ноль ',
        '1': ' один ',
        '2': ' два ',
        '3': ' три ',
        '4': ' чет+ыре ',
        '5': ' пять ',
        '6': ' шесть ',
        '7': ' семь ',
        '8': ' в+осемь ',
        '9': ' д+евять ',
    }

    return ''.join([translit_map.get(char, char) for char in text])

def float2text(number):
    # Разделяем число на целую и дробную части
    rubles, kopecks = divmod(number, 1)
    rubles = int(rubles)
    kopecks = int(round(kopecks * 100))

    # Преобразуем целую часть в текст
    rubles_text = num2words(rubles, lang='ru')
    kopecks_text = num2words(kopecks, lang='ru')

    # Формируем строку с правильными окончаниями
    rubles_text += " рубль" if rubles % 10 == 1 and rubles % 100 != 11 else \
                   " рубля" if 2 <= rubles % 10 <= 4 and (rubles % 100 < 10 or rubles % 100 >= 20) else \
                   " рублей"
    if kopecks > 0:
        kopecks_text += " копейка" if kopecks % 10 == 1 and kopecks % 100 != 11 else \
                        " копейки" if 2 <= kopecks % 10 <= 4 and (kopecks % 100 < 10 or kopecks % 100 >= 20) else \
                        " копеек"
    else:
        kopecks_text = ""
    return f"{rubles_text} {kopecks_text}"

def is_speak_xml(text):
    return text.strip().startswith("<speak>") and text.strip().endswith("</speak>")

class TTSGenerator():
	def __init__(self, sample_rate):
		self.sample_rate = sample_rate

		device = torch.device('cpu')
		torch.set_num_threads(4)
		local_file = 'v4_ru.pt'

		if not os.path.isfile(local_file):
			torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',
										local_file)
		self.model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
		self.model.to(device)


	def get_all_voices(self):
		return self.model.speakers
	
	def generate_voice_to_file(self, text, speaker, output_file):
		ssml_text = text if is_speak_xml(text) else None
		plain_text = None if is_speak_xml(text) else text
		return self.model.save_wav(text=plain_text, ssml_text=ssml_text,
                                speaker=speaker,
                                sample_rate=self.sample_rate,
                                audio_path=output_file)
		
	def generate_voice(self, text, speaker):
		ssml_text = text if is_speak_xml(text) else None
		plain_text = None if is_speak_xml(text) else text
		audio = self.model.apply_tts(text=plain_text, ssml_text=ssml_text,
                                speaker=speaker,
                                sample_rate=self.sample_rate)
		buffer = io.BytesIO()
		sf.write(buffer, audio.numpy(), self.sample_rate, format='WAV')
		buffer.seek(0)
		return buffer
	
