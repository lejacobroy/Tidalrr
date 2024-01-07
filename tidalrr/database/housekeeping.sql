/*** HOUEKEEPING 
	1. mark downloaded tracks (from files) as downloaded
	2. remove queues of downloaded tracks
***/

update tidal_tracks set queued = 0, downloaded = 1 where id in (
	select tidal_tracks.id from tidal_Tracks
	inner join files on files.id = tidal_tracks.id
	where tidal_tracks.downloaded = 0
);

update tidal_tracks set queued = 0 where id in (
	select tidal_tracks.id from tidal_Tracks
	inner join tidal_queue on tidal_queue.id = tidal_tracks.id
	where tidal_tracks.downloaded = 1 
);

delete from tidal_queue where id in (
	select tidal_tracks.id from tidal_Tracks
	inner join tidal_queue on tidal_queue.id = tidal_tracks.id
	where tidal_tracks.downloaded = 1 
);
VACUUM;