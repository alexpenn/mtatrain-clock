import time
import sys
import mta_notification

from samplebase import SampleBase
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from rgbmatrix import graphics

### graphics definitions
font = graphics.Font()
font.LoadFont("rpi-rgb-led-matrix/fonts/7x13B.bdf")

green = graphics.Color(0, 140, 0)
gray = graphics.Color(90,90,92)
white = graphics.Color(255,255,255)
blue = graphics.Color(0,0,160)

### station definitions
station1N = "L10N"
station1S = "L10S"
station2N = "G29N"
station2S = "G29S"
#L and G feeds
train1url = mta_notification.get_train_url('L')
train2url = mta_notification.get_train_url('G')

###how often to refresh feed
REFRESH_TIME = 60

###time to walk to station (in min)
WALK_TIME = 7

class timeBoard(object):
    def __init__(self):
        self.next1N = -1
        self.next1N2= -1
        self.next1S= -1
        self.next1S2= -1
        self.next2N= -1
        self.next2N2= -1
        self.next2S= -1
        self.next2S2= -1

        self.t1N = 'NR'
        self.t1S = 'NR'
        self.t2N = 'NR'
        self.t2S = 'NR'

    def formatData(self):
        self.t1N = str(self.next1N).zfill(2) + ',' + str(self.next1N2).zfill(2)
        self.t1S = str(self.next1S).zfill(2) + ',' + str(self.next1S2).zfill(2)
        self.t2N = str(self.next2N).zfill(2) + ',' + str(self.next2N2).zfill(2)
        self.t2S = str(self.next2S).zfill(2) + ',' + str(self.next2S2).zfill(2)

        

class mtatrainClock(SampleBase):
    def __init__(self, *args, **kwargs):
        super(mtatrainClock, self).__init__(*args,**kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Met-Lorimer")

    def pullData(self, arrivals):
        rtd1 = mta_notification.get_feed(train1url)
        rtd2 = mta_notification.get_feed(train2url)

        times1N = mta_notification.station_time_lookup(rtd1,station1N)
        times2S = mta_notification.station_time_lookup(rtd2,station2S)
        arrivals.next1N, arrivals.next1N2 = mta_notification.get_next_times(times1N,WALK_TIME)
        arrivals.next2S, arrivals.next2S2 = mta_notification.get_next_times(times2S,WALK_TIME)

        times1S = mta_notification.station_time_lookup(rtd1,station1S)
        times2N = mta_notification.station_time_lookup(rtd2,station2N)
        arrivals.next1S, arrivals.next1S2 = mta_notification.get_next_times(times1S,WALK_TIME)
        arrivals.next2N, arrivals.next2N2 = mta_notification.get_next_times(times2N,WALK_TIME)

        return arrivals
    
    def drawCircle(self, canvas,  x, y, color):
        # Draw circle with lines
        graphics.DrawLine(canvas, x+5, y+0, x+10, y+0, color)
        graphics.DrawLine(canvas, x+3, y+1, x+12, y+1, color)
        graphics.DrawLine(canvas, x+2, y+2, x+13, y+2, color)
        graphics.DrawLine(canvas, x+1, y+3, x+14, y+3, color)
        graphics.DrawLine(canvas, x+1, y+4, x+14, y+4, color)
        graphics.DrawLine(canvas, x+0, y+5, x+15, y+5, color)
        graphics.DrawLine(canvas, x+0, y+6, x+15, y+6, color)
        graphics.DrawLine(canvas, x+0, y+7, x+15, y+7, color)
        graphics.DrawLine(canvas, x+0, y+8, x+15, y+8, color)
        graphics.DrawLine(canvas, x+0, y+9, x+15, y+9, color)
        graphics.DrawLine(canvas, x+1, y+10, x+14, y+10, color)
        graphics.DrawLine(canvas, x+1, y+11, x+14, y+11, color)
        graphics.DrawLine(canvas, x+2, y+12, x+13, y+12, color)
        graphics.DrawLine(canvas, x+3, y+13, x+12, y+13, color)
        graphics.DrawLine(canvas, x+5, y+14, x+10, y+14, color)

    def drawL(self, matrix, pos):
        if pos=='top':
            self.drawCircle(matrix, 0,0, gray)
            graphics.DrawText(matrix, font, 5,12,white, "L")
        if pos=='bot':
            self.drawCircle(matrix, 0,16, gray)
            graphics.DrawText(matrix, font, 5,28,white, "L")

    def drawG(self, matrix, pos):
        if pos=='top':
            self.drawCircle(matrix, 0,0, green)
            graphics.DrawText(matrix, font, 5,12,white, "G")
        if pos=='bot':
            self.drawCircle(matrix, 0,16, green)
            graphics.DrawText(matrix, font, 5,28,white, "G")

    def returnStop(self, line,dir):
        if line=='L':
            if dir=='north':
                return '8TH AVE'
            elif dir=='south':
                return 'CANARSIE'
        elif line=='G':
            if dir=='north':
                return 'COURT SQ'
            elif dir=='south':
                return 'CHURCH ST'

    def drawNorth(self, canvas, arrivalstr):
        canvas.Clear()
        self.drawL(canvas, 'top')
        graphics.DrawText(canvas, font, 20, 12, white, self.returnStop('L','north'))
        graphics.DrawText(canvas, font, 90, 12, blue, arrivalstr.t1N)
        self.drawG(canvas, 'bot')
        graphics.DrawText(canvas, font, 20, 28, white, self.returnStop('G','south'))
        graphics.DrawText(canvas, font, 90, 28, blue, arrivalstr.t2S)


    def drawSouth(self, canvas, arrivalstr):
        canvas.Clear()
        self.drawL(canvas, 'top')
        graphics.DrawText(canvas, font, 20, 12, white, self.returnStop('L','south'))
        graphics.DrawText(canvas, font, 90, 12, blue, arrivalstr.t1S)
        self.drawG(canvas, 'bot')
        graphics.DrawText(canvas, font, 20, 28, white, self.returnStop('G','north'))
        graphics.DrawText(canvas, font, 90, 28, blue, arrivalstr.t2N)

    def run(self):
        i = 0
        canvas = self.matrix.CreateFrameCanvas()

        while True:
            canvas = self.matrix.CreateFrameCanvas()

            arrivals = timeBoard()

            self.pullData(arrivals)
            arrivals.formatData()

            if i%2 == 1:
                self.drawNorth(canvas, arrivals)
                # draw to the canvas
                canvas = self.matrix.SwapOnVSync(canvas)
                time.sleep(REFRESH_TIME*0.58)
            elif i%2 == 0:
                self.drawSouth(canvas, arrivals)
                # draw to the canvas
                canvas = self.matrix.SwapOnVSync(canvas)
                time.sleep(REFRESH_TIME*0.42)
            print(i)
            i = i + 1



# Main function
if __name__ == "__main__":
    mtatrain_clock = mtatrainClock()
    if (not mtatrain_clock.process()):
        mtatrain_clock.print_help()

