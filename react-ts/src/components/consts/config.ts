type ConfigType = {
  API_URL: string
}

const CONFIG: ConfigType = {
  API_URL: import.meta.env.VITE_API_URL || "/api"
}

export default CONFIG