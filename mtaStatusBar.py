import rumps
import mta_notification

#Metropolitan-Lorimer L & G station
station1N = "L10N"
station1S = "L10S"
station2N = "G29N"
station2S = "G29S"

#how often to refresh feed
REFRESH_TIME = 300

#time to walk to station
WALK_TIME = 6

#L and G feeds
train1url = mta_notification.get_train_url('L')
train2url = mta_notification.get_train_url('G')

rumps.debug_mode(True)

class mtaStatusBar(rumps.App):

    def __init__(self):
        super(mtaStatusBar, self).__init__(name='mtaStatusBar', icon='MTA-logo.png')
        self.menu = [rumps.MenuItem('to 8th', icon='L.png', dimensions=(18, 18)), 
                     rumps.MenuItem('to Church St', icon='G.png', dimensions=(18, 18)),
                     rumps.MenuItem('to Canarsie', icon='L.png', dimensions=(18, 18)),
                     rumps.MenuItem('to Court Sq', icon='G.png', dimensions=(18, 18)),
                     None]
        
    @rumps.timer(REFRESH_TIME)
    def pull_data(self, _):
        rtd1 = mta_notification.get_feed(train1url)
        rtd2 = mta_notification.get_feed(train2url)

        times1N = mta_notification.station_time_lookup(rtd1,station1N)
        times2S = mta_notification.station_time_lookup(rtd2,station2S)
        next1N, next1N2 = mta_notification.get_next_times(times1N,WALK_TIME)
        next2S, next2S2 = mta_notification.get_next_times(times2S,WALK_TIME)

        times1S = mta_notification.station_time_lookup(rtd1,station1S)
        times2N = mta_notification.station_time_lookup(rtd2,station2N)
        next1S, next1S2 = mta_notification.get_next_times(times1S,WALK_TIME)
        next2N, next2N2 = mta_notification.get_next_times(times2N,WALK_TIME)

        #print(next1N)
        self.title = str(next1N) + ' min'
        self.menu['to 8th'].title = 'to 8th: ' + str(next1N) + ' min, ' + str(next1N2) + ' min'
        self.menu['to Canarsie'].title = 'to Canarsie: ' + str(next1S) + ' min, ' + str(next1S2) + ' min'
        self.menu['to Church St'].title = 'to Church St: ' + str(next2S) + ' min, ' + str(next2S2) + ' min'
        self.menu['to Court Sq'].title = 'to Court Sq: ' + str(next2N) + ' min, ' + str(next2N2) + ' min'



if __name__ == "__main__":
    mtaStatusBar().run()