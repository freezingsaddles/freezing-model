import re
import warnings

from geoalchemy import LineString, Point, GeometryColumn, GeometryDDL
from sqlalchemy import orm, Column, BigInteger, Integer, String, Boolean, ForeignKey, DateTime, Float, Text, Time
from sqlalchemy.ext.declarative import declarative_base

from . import meta, satypes

Base = declarative_base(metadata=meta.metadata)


class _SqlView:
    """ Empty class used to indicate that this is a SQL View and not to be created. """
    pass


class StravaEntity(Base):
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}  # But we use MyISAM for the spatial table.

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String(1000), nullable=False)

    def __init__(self, id=None, name=None, **kwargs):
        self.id = id
        self.name = name
        for (k, v) in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                raise AttributeError("Unable to set attribute {0} on {1}".format(k, self.__class__.__name__))

    def __repr__(self):
        return '<{0} id={1} name={2!r}>'.format(self.__class__.__name__, self.id, self.name)


class Team(StravaEntity):
    """
    """
    __tablename__ = 'teams'
    athletes = orm.relationship("Athlete", backref="team")
    leaderboard_exclude = Column(Boolean, nullable=False, default=False)


class Athlete(StravaEntity):
    """
    """
    __tablename__ = 'athletes'
    display_name = Column(String(255), nullable=True)
    team_id = Column(BigInteger, ForeignKey('teams.id', ondelete='set null'))
    access_token = Column(String(255), nullable=True)
    profile_photo = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    expires_at = Column(BigInteger, default=0)

    rides = orm.relationship("Ride", backref="athlete", lazy="dynamic", cascade="all, delete, delete-orphan")


class RideError(StravaEntity):
    """
    """
    __tablename__ = 'ride_errors'
    athlete_id = Column(BigInteger, ForeignKey('athletes.id', ondelete='cascade'), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)  # 2010-02-28T08:31:35Z
    last_seen = Column(DateTime, nullable=False, index=True)
    reason = Column(String(1024), nullable=False)


class Ride(StravaEntity):
    """
    """
    __tablename__ = 'rides'
    athlete_id = Column(BigInteger, ForeignKey('athletes.id', ondelete='cascade'), nullable=False, index=True)
    elapsed_time = Column(Integer, nullable=False)  # Seconds
    # in case we want to conver that to a TIME type ... (using time for interval is kinda mysql-specific brokenness, though)
    # time.strftime('%H:%M:%S', time.gmtime(12345))
    moving_time = Column(Integer, nullable=False, index=True)  #
    elevation_gain = Column(Integer, nullable=True)  # 269.6 (feet)
    average_speed = Column(Float)  # mph
    maximum_speed = Column(Float)  # mph
    start_date = Column(DateTime, nullable=False, index=True)  # 2010-02-28T08:31:35Z
    distance = Column(Float, nullable=False, index=True)  # 82369.1 (meters)
    location = Column(String(255), nullable=True)

    commute = Column(Boolean, nullable=True)
    trainer = Column(Boolean, nullable=True)

    efforts_fetched = Column(Boolean, default=False, nullable=False)

    timezone = Column(String(255), nullable=True)

    geo = orm.relationship("RideGeo", uselist=False, backref="ride", cascade="all, delete, delete-orphan")
    weather = orm.relationship("RideWeather", uselist=False, backref="ride", cascade="all, delete, delete-orphan")
    photos = orm.relationship("RidePhoto", backref="ride", cascade="all, delete, delete-orphan")
    track = orm.relationship("RideTrack", uselist=False, backref="ride", cascade="all, delete, delete-orphan")

    photos_fetched = Column(Boolean, default=None, nullable=True)
    track_fetched = Column(Boolean, default=None, nullable=True)
    detail_fetched = Column(Boolean, default=False, nullable=False)

    private = Column(Boolean, default=False, nullable=False)
    manual = Column(Boolean, default=None, nullable=True)


# Broken out into its own table due to MySQL (5.0/1.x, anyway) not allowing NULL values in geometry columns.
class RideGeo(Base):
    __tablename__ = 'ride_geo'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}  # MyISAM for spatial indexes

    ride_id = Column(BigInteger, ForeignKey('rides.id'), primary_key=True)
    start_geo = GeometryColumn(Point(2), nullable=False)
    end_geo = GeometryColumn(Point(2), nullable=False)

    def __repr__(self):
        return '<{0} ride_id={1} start={2}>'.format(self.__class__.__name__,
                                                    self.ride_id,
                                                    self.start_geo)


# Broken out into its own table due to MySQL (5.0/1.x, anyway) not allowing NULL values in geometry columns.
class RideTrack(Base):
    __tablename__ = 'ride_tracks'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8mb4'}  # MyISAM for spatial indexes

    ride_id = Column(BigInteger, ForeignKey('rides.id'), primary_key=True)
    gps_track = GeometryColumn(LineString(2), nullable=False)
    elevation_stream = Column(satypes.JSONEncodedText, nullable=True)
    time_stream = Column(satypes.JSONEncodedText, nullable=True)

    def __repr__(self):
        return '<{0} ride_id={1}>'.format(self.__class__.__name__, self.ride_id)


class RideEffort(Base):
    __tablename__ = 'ride_efforts'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}  # MyISAM for spatial indexes
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    ride_id = Column(BigInteger, ForeignKey('rides.id', ondelete="cascade"), index=True)
    segment_name = Column(String(255), nullable=False)
    segment_id = Column(BigInteger, nullable=False, index=True)
    elapsed_time = Column(Integer, nullable=False)

    def __repr__(self):
        return '<{} id={} segment_name={!r}>'.format(self.__class__.__name__, self.id, self.segment_name)


class RidePhoto(Base):
    __tablename__ = 'ride_photos'

    id = Column(String(191), primary_key=True, autoincrement=False)
    source = Column(Integer, nullable=False, default=2)
    ride_id = Column(BigInteger, ForeignKey('rides.id', ondelete="cascade"), index=True)
    ref = Column(String(255), nullable=True)
    caption = Column(Text, nullable=True)

    img_t = Column(String(255), nullable=True)
    img_l = Column(String(255), nullable=True)

    @property
    def img_l_dimensions(self):
        (width, height) = (None, None)
        if self.img_l:
            if self.source == 1:
                try:
                    (width, height) = re.match('.+-(\d+)x(\d+)\.\w+$', self.img_l).groups()
                except AttributeError:
                    warnings.warn("Unable to get width and height from source=1 image url: {}".format(self.img_l))
            else:
                (width, height) = (612, 612)
        return (width, height)

    primary = Column(Boolean, nullable=False, default=False)

    # upload_date = Column(DateTime, nullable=False, index=True) # 2010-02-28T08:31:35Z

    def __repr__(self):
        return '<{} id={} primary={!r}>'.format(self.__class__.__name__, self.id, self.primary)


class RideWeather(Base):
    __tablename__ = 'ride_weather'
    ride_id = Column(BigInteger, ForeignKey('rides.id'), primary_key=True)

    ride_temp_start = Column(Float, nullable=True)
    ride_temp_end = Column(Float, nullable=True)
    ride_temp_avg = Column(Float, nullable=True)

    ride_windchill_start = Column(Float, nullable=True)
    ride_windchill_end = Column(Float, nullable=True)
    ride_windchill_avg = Column(Float, nullable=True)

    ride_precip = Column(Float, nullable=True)  # In inches
    ride_rain = Column(Boolean, default=False, nullable=False)
    ride_snow = Column(Boolean, default=False, nullable=False)

    day_temp_min = Column(Float, nullable=True)
    day_temp_max = Column(Float, nullable=True)

    sunrise = Column(Time, nullable=True)
    sunset = Column(Time, nullable=True)

    def __repr__(self):
        return '<{0} ride_id={1}>'.format(self.__class__.__name__, self.id, self.segment_name)


# Setup Geometry columns
GeometryDDL(RideGeo.__table__)
GeometryDDL(RideTrack.__table__)

# Opting for a more explicit approach to specifyign which tables are to be managed by SA.
#
# _MANAGED_TABLES = [obj.__table__ for name, obj in inspect.getmembers(sys.modules[__name__])
#                   if inspect.isclass(obj) and (issubclass(obj, Base) and obj is not Base)
#                   and hasattr(obj, '__table__')
#                   and not issubclass(obj, _SqlView)]
#
# register_managed_tables(_MANAGED_TABLES)
