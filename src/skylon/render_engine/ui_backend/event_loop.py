import sdl2 as sdl
from ctypes import byref as pointer


def sdl_event_loop():
    event = sdl.SDL_Event()
    running = True

    while running:
        event_pointer = pointer(event)
        pending_events = sdl.SDL_PollEvent(event_pointer)
        while pending_events:

            # QUIT HANDLER
            if event.type == sdl.SDL_QUIT:
                running = False
                sdl.SDL_Quit()
                break

            # UPDATE PENDING EVENTS
            pending_events = sdl.SDL_PollEvent(event_pointer)
        sdl.SDL_WaitEvent(event_pointer)
