import sdl2 as sdl
from ctypes import byref as pointer


def sdl_event_loop(handlers):
    handled_events = handlers.keys()
    event = sdl.SDL_Event()

    while True:
        sdl.SDL_WaitEvent(pointer(event))

        if event.type == sdl.SDL_QUIT:
            break

        elif event.type in handled_events:
            handlers[event.type](event)
