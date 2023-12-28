import { Evented, type LatLng } from "leaflet";

export interface BboxLatLng {
    ne: LatLng,
    sw: LatLng
}

export enum ExcludeIncludeLabelPrompt {
    ExcludeMarkerPrompt = 0,
    IncludeMarkerPrompt = 1
}
type PointPromptType = "point"
type RectanglePromptType = "rectangle"

export interface IPointPrompt {
    id: Evented.layer._url,
    type: PointPromptType,
    data: LatLng,
    label: ExcludeIncludeLabelPrompt
}

export interface IRectanglePrompt {
    id?: Evented.layer._url,
    type: RectanglePromptType,
    data: BboxLatLng
}

export interface IPointTable {
    id?: Evented.layer._url,
    data: LatLng,
    label: ExcludeIncludeLabelPrompt
}

export interface IRectangleTable {
    id?: Evented.layer._url,
    data_ne: BboxLatLng,
    data_sw: BboxLatLng
}
  
export interface IBodyLatLngPoints {
    bbox: BboxLatLng,
    prompt: Array<IPointPrompt|IRectanglePrompt>,
    zoom: number,
    source_type: string
}

export type OpenStreetMap = "OpenStreetMap"
export type Satellite = "Satellite"
export type SourceTileType = OpenStreetMap | Satellite
export type ArrayNumber = Array<number>