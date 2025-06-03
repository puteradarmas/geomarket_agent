import React, { useCallback, useState } from 'react'
import { GoogleMap, Marker, useLoadScript,useJsApiLoader  } from '@react-google-maps/api'

const libraries = ['places']
const mapContainerStyle = {
  width: '100%',
  height: '400px',
}
const center = {
  lat: -6.2, // default center (Jakarta, etc.)
  lng: 106.8,
}

type Props = {
  onLocationSelect: (location: { lat: number; lng: number, }) => void
}

const LocationPicker: React.FC<Props> = ({ onLocationSelect }) => {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: 'AIzaSyBmugJei5MXFJu2525l8Bh6cPNJKUtWcS4', // 🔑 Replace with your key
  });

  const [marker, setMarker] = useState<{ lat: number; lng: number } | null>(null)

  const onMapClick = useCallback((e: google.maps.MapMouseEvent) => {
    const lat = e.latLng?.lat()
    const lng = e.latLng?.lng()
    if (lat && lng) {
      setMarker({ lat, lng })
      onLocationSelect({ lat, lng })
    }
  }, [onLocationSelect])


  if (loadError) return <div>Error loading map</div>
  if (!isLoaded) return <div>Loading map...</div>

  const mapOptions = {
  disableDefaultUI: true,
  zoomControl: true,
  };

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      zoom={10}
      center={marker || center}
      onClick={onMapClick}
      options={mapOptions}
    >
      {marker && <Marker position={marker} />}
    </GoogleMap>
  );
}

export default LocationPicker