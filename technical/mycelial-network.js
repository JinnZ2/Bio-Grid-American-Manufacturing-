// BioGrid: Mycelial Underground Fiber + Energy Distribution Network

export const mycelialNetwork = {
  undergroundLength_km: 15000,
  underwaterCrossings: {
    lakeMichigan: { from: 'Milwaukee', to: 'Muskegon', length_km: 120, depth_m: 85, type: '±500kV HVDC' },
    lakeErie: { from: 'Cleveland', to: 'Ontario', length_km: 75, depth_m: 65 },
    lakeSuperior: { from: 'Duluth', to: 'Thunder Bay', length_km: 200, depth_m: 150 }
  },

  constructionMethods: ['directBurial', 'ductBank', 'HDD', 'TBM'],
  cableSpecs: {
    transmission: { voltage: '138–765kV', ampacity: '1000–3000A', life: '40+ yrs' },
    distribution: { voltage: '12.47–34.5kV', ampacity: '200–800A' },
    fiber: { capacity: '10+ Tbps', fibers: 288 }
  },

  protection: {
    thermalMonitoring: true,
    environmentalMitigation: ['wetlands
