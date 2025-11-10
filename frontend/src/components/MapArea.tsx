
import { useEffect, useRef, useState } from "react"

declare global {
  interface Window {
    AMap: any
  }
}

const MapArea = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any>(null)
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null)
  const [mapReady, setMapReady] = useState(false)

  // 获取用户当前位置
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          setUserLocation([longitude, latitude])
        },
        (error) => {
          console.error("获取位置失败:", error)
          // 如果获取位置失败，使用默认位置（北京天安门）
          setUserLocation([116.397428, 39.90923])
        }
      )
    } else {
      console.error("浏览器不支持地理定位")
      // 如果不支持地理定位，使用默认位置（北京天安门）
      setUserLocation([116.397428, 39.90923])
    }
  }, [])

  // 初始化地图
  useEffect(() => {
    if (mapContainerRef.current && !mapRef.current && window.AMap && userLocation) {
      mapRef.current = new window.AMap.Map(mapContainerRef.current, {
        zoom: 15,
        center: userLocation, // 使用用户当前位置
        mapStyle: "amap://styles/light" // 浅色主题
      })

      // 添加当前位置标记点
      const userMarker = new window.AMap.Marker({
        position: userLocation,
        title: "我的位置",
        icon: new window.AMap.Icon({
          image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
          size: new window.AMap.Size(25, 34),
          imageSize: new window.AMap.Size(25, 34)
        })
      })
      mapRef.current.add(userMarker)

      // 添加另一个标记点示例
      const marker2 = new window.AMap.Marker({
        position: [userLocation[0] + 0.01, userLocation[1] + 0.01],
        title: "附近地点"
      })
      mapRef.current.add(marker2)

      setMapReady(true)
    }

    return () => {
      // 清理地图实例
      if (mapRef.current) {
        mapRef.current.destroy()
        mapRef.current = null
      }
    }
  }, [userLocation])

  const handleSearch = () => {
    // 模拟搜索功能，随机改变地图中心点
    if (mapRef.current && userLocation) {
      const randomLng = userLocation[0] + (Math.random() - 0.5) * 0.1
      const randomLat = userLocation[1] + (Math.random() - 0.5) * 0.1
      mapRef.current.setCenter([randomLng, randomLat])
    }
    // TODO: Integrate backend for POI search
  }

  const handleBackToCurrentLocation = () => {
    // 返回当前位置
    if (mapRef.current && userLocation) {
      mapRef.current.setCenter(userLocation)
      mapRef.current.setZoom(15)
    }
  }

  return (
    <div className="relative h-full">
      {/* 顶部搜索栏 */}
      <div className="absolute top-4 left-4 right-4 z-10 bg-white rounded-lg shadow-md p-3 flex items-center space-x-2">
        <input
          type="text"
          placeholder="出发地"
          className="border rounded px-2 py-1 flex-1"
        />
        <input
          type="text"
          placeholder="目的地"
          className="border rounded px-2 py-1 flex-1"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600"
        >
          搜索
        </button>
        {mapReady && (
          <button
            onClick={handleBackToCurrentLocation}
            className="bg-green-500 text-white px-4 py-1 rounded hover:bg-green-600"
            title="返回当前位置"
          >
            定位
          </button>
        )}
      </div>

      {/* 地图容器 */}
      <div id="map-container" ref={mapContainerRef} className="w-full h-full"></div>
    </div>
  )
}

export default MapArea
