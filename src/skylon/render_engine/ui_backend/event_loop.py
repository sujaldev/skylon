import sdl2 as sdl
from ctypes import byref as pointer


def sdl_event_loop():
    event = sdl.SDL_Event()
    running = True

    while running:
        pending_events = sdl.SDL_PollEvent(pointer(event))
        while pending_events != 0:

            # QUIT HANDLER
            if event.type == sdl.SDL_QUIT:
                running = False
                sdl.SDL_Quit()
                break

            # UPDATE PENDING EVENTS
            pending_events = sdl.SDL_PollEvent(pointer(event))
