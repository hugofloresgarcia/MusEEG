from pyOpenBCI import OpenBCICyton

def print_raw(sample):
    print(sample.channels_data)

# port = OpenBCICyton.find_port()
board = OpenBCICyton(port='/dev/tty.usbserial-DM0258BS', daisy=True)

board.start_stream(print_raw)