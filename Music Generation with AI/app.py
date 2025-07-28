from flask import Flask, render_template, send_file, request
from music21 import converter, instrument, note, chord, stream
import numpy as np
import tensorflow as tf
import os
import random

app = Flask(__name__)

def load_notes():
    notes = []
    for file in os.listdir("model"):
        if file.endswith(".mid"):
            midi = converter.parse(f"model/{file}")
            parts = instrument.partitionByInstrument(midi)
            notes_to_parse = parts.parts[0].recurse() if parts else midi.flat.notes
            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))
    return notes

def prepare_sequences(notes, seq_length=100):
    pitchnames = sorted(set(notes))
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))
    network_input = []
    for i in range(len(notes) - seq_length):
        sequence_in = notes[i:i + seq_length]
        network_input.append([note_to_int[char] for char in sequence_in])
    return network_input, note_to_int, pitchnames

def create_model(input_shape, n_vocab):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(512, input_shape=input_shape, return_sequences=True),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.LSTM(512),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(n_vocab, activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

def generate_music():
    notes = load_notes()
    network_input, note_to_int, pitchnames = prepare_sequences(notes)
    n_vocab = len(set(notes))

    X = np.reshape(network_input, (len(network_input), len(network_input[0]), 1)) / float(n_vocab)
    y = tf.keras.utils.to_categorical([note_to_int[n] for n in notes[100:100 + len(network_input)]], num_classes=n_vocab)

    model = create_model((X.shape[1], X.shape[2]), n_vocab)
    model.fit(X, y, epochs=5, batch_size=64, verbose=0)

    start = random.randint(0, len(network_input)-1)
    pattern = network_input[start]
    prediction_output = []

    for _ in range(200):
        prediction_input = np.reshape(pattern, (1, len(pattern), 1)) / float(n_vocab)
        prediction = model.predict(prediction_input, verbose=0)
        index = np.argmax(prediction)
        result = pitchnames[index]
        prediction_output.append(result)
        pattern.append(index)
        pattern = pattern[1:]

    offset = 0
    output_notes = []
    for pattern in prediction_output:
        if '.' in pattern or pattern.isdigit():
            notes_in_chord = [note.Note(int(n)) for n in pattern.split('.')]
            new_chord = chord.Chord(notes_in_chord)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            output_notes.append(new_note)
        offset += 0.5

    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp='generated_music.mid')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    generate_music()
    return send_file('generated_music.mid', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
