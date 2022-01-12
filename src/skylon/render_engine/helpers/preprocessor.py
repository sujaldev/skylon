"""
THIS MODULE REMOVES UNNECESSARY CHARACTERS FROM THE INPUT STREAM

THE SPECIFICATION FOR PREPROCESSING HTML IS DEFINED HERE:
https://html.spec.whatwg.org/multipage/parsing.html#preprocessing-the-input-stream

THE SPECIFICATION FOR PREPROCESSING CSS IS DEFINED HERE:
https://www.w3.org/TR/css-syntax-3/#input-preprocessing
"""
from render_engine.helpers.CONSTANTS import CARRIAGE_RETURN, NEWLINE, NULL, REPLACEMENT_CHARACTER


# TODO: IMPLEMENT HTML PREPROCESSOR NON CHAR HANDLING
def handle_non_char():
    pass


# TODO: IMPLEMENT HTML PREPROCESSOR NON CONTROL CHAR HANDLING
def handle_control_chars():
    pass


def normalize_newlines(source):
    normalized = source.replace(CARRIAGE_RETURN + NEWLINE, NEWLINE).replace(CARRIAGE_RETURN, NEWLINE)
    return normalized


def preprocess_html(source):
    handle_non_char()
    handle_control_chars()
    processed_stream = normalize_newlines(source)
    return processed_stream


def preprocess_css(source):
    preprocessed_stream = normalize_newlines(source)
    preprocessed_stream.replace(NULL, REPLACEMENT_CHARACTER)
    return preprocessed_stream
