import { Injectable } from '@angular/core';

export interface LabMarkerInfo {
  name: string;
  description: string;
  clinicalSignificance: string;
  fallbackReferenceRange: string;
  unit: string;
  category: string;
  lowMeaning?: string;
  highMeaning?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LabMarkerInfoService {
  
  private labMarkers: { [key: string]: LabMarkerInfo } = {
    // Complete Blood Count (CBC)
    'hémoglobine': {
      name: 'Hémoglobine',
      description: 'Protein in red blood cells that carries oxygen throughout your body. Essential for oxygen transport from lungs to tissues.',
      clinicalSignificance: 'Low levels indicate anemia (iron deficiency, chronic disease). High levels may suggest dehydration, lung disease, or polycythemia.',
      fallbackReferenceRange: '13.0 - 18.0',
      unit: 'g/dL',
      category: 'Blood Count',
      lowMeaning: 'May indicate anemia, blood loss, or nutritional deficiency',
      highMeaning: 'May indicate dehydration, lung disease, or blood disorders'
    },
    'hématocrite': {
      name: 'Hématocrite',
      description: 'Percentage of blood volume occupied by red blood cells. Reflects the proportion of blood that consists of red blood cells.',
      clinicalSignificance: 'Low values suggest anemia or blood loss. High values may indicate dehydration or polycythemia.',
      fallbackReferenceRange: '40.0 - 54.0',
      unit: '%',
      category: 'Blood Count',
      lowMeaning: 'Possible anemia or blood loss',
      highMeaning: 'Possible dehydration or blood thickening'
    },
    'globules rouges': {
      name: 'Globules rouges (Red Blood Cells)',
      description: 'Red blood cells that carry oxygen from lungs to body tissues and return carbon dioxide to lungs.',
      clinicalSignificance: 'Low count indicates anemia. High count may suggest dehydration, lung disease, or bone marrow disorders.',
      fallbackReferenceRange: '4.00 - 6.00',
      unit: '10^6/mm³',
      category: 'Blood Count',
      lowMeaning: 'Anemia or blood loss',
      highMeaning: 'Dehydration or blood disorders'
    },
    'vgm': {
      name: 'VGM (Mean Corpuscular Volume)',
      description: 'Average size of red blood cells. Helps classify types of anemia and blood disorders.',
      clinicalSignificance: 'Low VGM suggests iron deficiency anemia. High VGM may indicate B12/folate deficiency or liver disease.',
      fallbackReferenceRange: '80.0 - 98.0',
      unit: 'μm³',
      category: 'Blood Indices',
      lowMeaning: 'Iron deficiency or thalassemia',
      highMeaning: 'B12/folate deficiency or liver disease'
    },
    'hcm': {
      name: 'HCM (Mean Corpuscular Hemoglobin)',
      description: 'Average amount of hemoglobin in each red blood cell. Helps evaluate anemia types.',
      clinicalSignificance: 'Low values suggest iron deficiency. High values may indicate B12/folate deficiency.',
      fallbackReferenceRange: '27.0 - 34.0',
      unit: 'pg',
      category: 'Blood Indices',
      lowMeaning: 'Iron deficiency anemia',
      highMeaning: 'B12/folate deficiency'
    },
    'mchc': {
      name: 'MCHC (Mean Corpuscular Hemoglobin Concentration)',
      description: 'Concentration of hemoglobin in red blood cells. Indicates how well red blood cells are filled with hemoglobin.',
      clinicalSignificance: 'Low MCHC suggests iron deficiency. High MCHC may indicate spherocytosis or severe dehydration.',
      fallbackReferenceRange: '31.5 - 36.0',
      unit: '%',
      category: 'Blood Indices',
      lowMeaning: 'Iron deficiency or chronic disease',
      highMeaning: 'Rare blood disorders or severe dehydration'
    },
    'globules blancs': {
      name: 'Globules blancs (White Blood Cells)',
      description: 'Immune system cells that fight infections and diseases. Part of your body\'s defense system.',
      clinicalSignificance: 'Low count increases infection risk. High count may indicate infection, inflammation, or blood disorders.',
      fallbackReferenceRange: '4.00 - 10.00',
      unit: '10³/mm³',
      category: 'Blood Count',
      lowMeaning: 'Weakened immune system or bone marrow problems',
      highMeaning: 'Infection, inflammation, or blood disorders'
    },
    'neutrophiles': {
      name: 'Neutrophiles',
      description: 'Most common type of white blood cell. First responders to bacterial infections and inflammation.',
      clinicalSignificance: 'Low levels increase bacterial infection risk. High levels suggest bacterial infection or stress response.',
      fallbackReferenceRange: '45.0 - 75.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Increased infection risk',
      highMeaning: 'Bacterial infection or stress'
    },
    'lymphocytes': {
      name: 'Lymphocytes',
      description: 'White blood cells that fight viral infections and produce antibodies. Include T-cells and B-cells.',
      clinicalSignificance: 'Low levels may indicate immunodeficiency. High levels suggest viral infection or certain blood cancers.',
      fallbackReferenceRange: '12.0 - 48.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Immunodeficiency or chronic stress',
      highMeaning: 'Viral infection or blood disorders'
    },
    'monocytes': {
      name: 'Monocytes',
      description: 'Large white blood cells that become macrophages and fight chronic infections and inflammation.',
      clinicalSignificance: 'High levels may indicate chronic infection, inflammatory conditions, or certain blood disorders.',
      fallbackReferenceRange: '2.0 - 10.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Generally not clinically significant',
      highMeaning: 'Chronic infection or inflammatory disease'
    },
    'eosinophiles': {
      name: 'Eosinophiles',
      description: 'White blood cells that fight parasitic infections and are involved in allergic reactions.',
      clinicalSignificance: 'High levels suggest allergies, parasitic infections, or certain autoimmune conditions.',
      fallbackReferenceRange: '0.0 - 6.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Normal finding',
      highMeaning: 'Allergies, parasites, or autoimmune disease'
    },
    'basophiles': {
      name: 'Basophiles',
      description: 'Least common white blood cells involved in allergic reactions and inflammation.',
      clinicalSignificance: 'High levels may indicate allergic reactions or certain blood disorders.',
      fallbackReferenceRange: '0.0 - 2.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Normal finding',
      highMeaning: 'Allergic reactions or blood disorders'
    },
    'luc': {
      name: 'LUC (Large Unstained Cells)',
      description: 'Immature or abnormal white blood cells detected by automated analyzers.',
      clinicalSignificance: 'High levels may indicate viral infections, stress, or blood disorders requiring further investigation.',
      fallbackReferenceRange: '0.0 - 5.0',
      unit: '%',
      category: 'White Blood Cell Differential',
      lowMeaning: 'Normal finding',
      highMeaning: 'Viral infection or blood disorder'
    },
    'plaquettes': {
      name: 'Plaquettes (Platelets)',
      description: 'Blood cells responsible for clotting and stopping bleeding when injuries occur.',
      clinicalSignificance: 'Low count increases bleeding risk. High count may increase clotting risk or indicate bone marrow disorders.',
      fallbackReferenceRange: '150 - 450',
      unit: '10³/mm³',
      category: 'Blood Count',
      lowMeaning: 'Increased bleeding risk',
      highMeaning: 'Increased clotting risk or bone marrow disorder'
    },

    // Iron Studies
    'fer': {
      name: 'Fer (Iron)',
      description: 'Essential mineral needed for hemoglobin production and oxygen transport.',
      clinicalSignificance: 'Low levels indicate iron deficiency anemia. High levels may suggest hemochromatosis or liver disease.',
      fallbackReferenceRange: '65 - 175',
      unit: 'μg/dL',
      category: 'Iron Studies',
      lowMeaning: 'Iron deficiency anemia',
      highMeaning: 'Iron overload or liver disease'
    },
    'ferritine': {
      name: 'Ferritine (Ferritin)',
      description: 'Protein that stores iron in your body. Best indicator of total body iron stores.',
      clinicalSignificance: 'Low levels indicate iron deficiency. High levels may suggest inflammation, liver disease, or iron overload.',
      fallbackReferenceRange: '22 - 322',
      unit: 'μg/L',
      category: 'Iron Studies',
      lowMeaning: 'Iron deficiency',
      highMeaning: 'Inflammation, liver disease, or iron overload'
    },

    // Vitamins
    'vitamine b12': {
      name: 'Vitamine B12',
      description: 'Essential vitamin for nerve function, DNA synthesis, and red blood cell formation.',
      clinicalSignificance: 'Low levels cause pernicious anemia and neurological problems. High levels are usually not harmful.',
      fallbackReferenceRange: '211 - 911',
      unit: 'ng/L',
      category: 'Vitamins',
      lowMeaning: 'B12 deficiency anemia and nerve damage',
      highMeaning: 'Usually not clinically significant'
    },
    '25 oh vitamine d': {
      name: '25-OH Vitamine D',
      description: 'Storage form of vitamin D. Essential for bone health, immune function, and calcium absorption.',
      clinicalSignificance: 'Low levels cause bone weakness and increased infection risk. Optimal levels support bone and immune health.',
      fallbackReferenceRange: '20 - 50',
      unit: 'ng/mL',
      category: 'Vitamins',
      lowMeaning: 'Bone weakness and increased infection risk',
      highMeaning: 'Generally beneficial, rarely toxic'
    },

    // Metabolic Panel
    'glycémie à jeun': {
      name: 'Glycémie à jeun (Fasting Glucose)',
      description: 'Blood sugar level after fasting. Primary screening test for diabetes and prediabetes.',
      clinicalSignificance: 'High levels indicate diabetes or prediabetes. Low levels may suggest hypoglycemia or insulin overdose.',
      fallbackReferenceRange: '60 - 99',
      unit: 'mg/dL',
      category: 'Metabolic',
      lowMeaning: 'Hypoglycemia - requires immediate attention',
      highMeaning: 'Prediabetes (100-125) or diabetes (≥126)'
    },
    'insulinémie à jeun': {
      name: 'Insulinémie à jeun (Fasting Insulin)',
      description: 'Hormone that regulates blood sugar. Measured to assess insulin resistance and diabetes risk.',
      clinicalSignificance: 'High levels suggest insulin resistance or type 2 diabetes risk. Low levels may indicate type 1 diabetes.',
      fallbackReferenceRange: '3.0 - 25.0',
      unit: 'mUI/L',
      category: 'Metabolic',
      lowMeaning: 'Possible type 1 diabetes',
      highMeaning: 'Insulin resistance or type 2 diabetes risk'
    },

    // Kidney Function
    'urée': {
      name: 'Urée (Urea)',
      description: 'Waste product filtered by kidneys. Indicator of kidney function and protein metabolism.',
      clinicalSignificance: 'High levels suggest kidney dysfunction or dehydration. Low levels may indicate liver disease or low protein intake.',
      fallbackReferenceRange: '13 - 43',
      unit: 'mg/dL',
      category: 'Kidney Function',
      lowMeaning: 'Liver disease or malnutrition',
      highMeaning: 'Kidney dysfunction or dehydration'
    },
    'créatinine': {
      name: 'Créatinine (Creatinine)',
      description: 'Waste product from muscle metabolism. Most reliable indicator of kidney function.',
      clinicalSignificance: 'High levels indicate kidney dysfunction. Normal levels suggest good kidney function.',
      fallbackReferenceRange: '0.70 - 1.30',
      unit: 'mg/dL',
      category: 'Kidney Function',
      lowMeaning: 'Low muscle mass (usually not concerning)',
      highMeaning: 'Kidney dysfunction'
    },

    'egfr': {
      name: 'eGFR (Estimated Glomerular Filtration Rate)',
      description: 'Calculated measure of kidney function based on creatinine, age, gender, and race.',
      clinicalSignificance: 'Lower values indicate reduced kidney function. Values <60 suggest chronic kidney disease.',
      fallbackReferenceRange: '> 60',
      unit: 'mL/min/1.73m²',
      category: 'Kidney Function',
      lowMeaning: 'Chronic kidney disease',
      highMeaning: 'Good kidney function'
    },
    'acide urique': {
      name: 'Acide urique (Uric Acid)',
      description: 'Waste product from purine metabolism. High levels can cause gout and kidney stones.',
      clinicalSignificance: 'High levels cause gout attacks and kidney stones. Low levels are usually not concerning.',
      fallbackReferenceRange: '3.5 - 7.2',
      unit: 'mg/dL',
      category: 'Kidney Function',
      lowMeaning: 'Usually not clinically significant',
      highMeaning: 'Gout risk and kidney stone formation'
    },

    // Electrolytes
    'sodium': {
      name: 'Sodium',
      description: 'Essential electrolyte for fluid balance, nerve function, and muscle contraction.',
      clinicalSignificance: 'Imbalances can cause serious neurological symptoms. Critical for maintaining blood pressure.',
      fallbackReferenceRange: '136 - 145',
      unit: 'mmol/L',
      category: 'Electrolytes',
      lowMeaning: 'Hyponatremia - confusion, seizures',
      highMeaning: 'Hypernatremia - dehydration, brain dysfunction'
    },
    'potassium': {
      name: 'Potassium',
      description: 'Essential electrolyte for heart rhythm, muscle function, and nerve transmission.',
      clinicalSignificance: 'Critical for heart function. Both high and low levels can cause dangerous heart rhythm abnormalities.',
      fallbackReferenceRange: '3.5 - 5.1',
      unit: 'mmol/L',
      category: 'Electrolytes',
      lowMeaning: 'Heart rhythm problems, muscle weakness',
      highMeaning: 'Heart rhythm problems, kidney dysfunction'
    },
    'chlore': {
      name: 'Chlore (Chloride)',
      description: 'Electrolyte that helps maintain fluid balance and acid-base balance in the body.',
      clinicalSignificance: 'Usually changes with sodium. Helps assess acid-base disorders and fluid balance.',
      fallbackReferenceRange: '98 - 108',
      unit: 'mmol/L',
      category: 'Electrolytes',
      lowMeaning: 'Fluid loss or acid-base imbalance',
      highMeaning: 'Dehydration or kidney dysfunction'
    },
    'bicarbonate': {
      name: 'Bicarbonate',
      description: 'Buffer that helps maintain blood pH. Important for acid-base balance.',
      clinicalSignificance: 'Low levels suggest acidosis. High levels suggest alkalosis. Both can be life-threatening.',
      fallbackReferenceRange: '22 - 29',
      unit: 'mmol/L',
      category: 'Electrolytes',
      lowMeaning: 'Metabolic acidosis',
      highMeaning: 'Metabolic alkalosis'
    },
    'calcium (total)': {
      name: 'Calcium (total)',
      description: 'Essential mineral for bone health, muscle function, nerve transmission, and blood clotting.',
      clinicalSignificance: 'Low levels cause muscle spasms and bone problems. High levels can cause kidney stones and heart problems.',
      fallbackReferenceRange: '2.15 - 2.65',
      unit: 'mmol/L',
      category: 'Electrolytes',
      lowMeaning: 'Bone disease, vitamin D deficiency',
      highMeaning: 'Kidney stones, heart rhythm problems'
    },

    // Lipid Panel
    'triglycérides': {
      name: 'Triglycérides (Triglycerides)',
      description: 'Type of fat in blood. High levels increase heart disease and pancreatitis risk.',
      clinicalSignificance: 'High levels increase cardiovascular risk and can cause pancreatitis if very high.',
      fallbackReferenceRange: '75 - 200',
      unit: 'mg/dL',
      category: 'Lipids',
      lowMeaning: 'Generally beneficial',
      highMeaning: 'Increased heart disease and pancreatitis risk'
    },
    'cholestérol total': {
      name: 'Cholestérol total (Total Cholesterol)',
      description: 'Total amount of cholesterol in blood. Includes both good (HDL) and bad (LDL) cholesterol.',
      clinicalSignificance: 'High levels increase heart disease risk. Optimal levels reduce cardiovascular events.',
      fallbackReferenceRange: '< 190',
      unit: 'mg/dL',
      category: 'Lipids',
      lowMeaning: 'Beneficial for heart health',
      highMeaning: 'Increased heart disease risk'
    },
    'cholestérol ldl': {
      name: 'Cholestérol LDL (Bad Cholesterol)',
      description: '"Bad" cholesterol that builds up in arteries and causes heart disease.',
      clinicalSignificance: 'High levels significantly increase heart attack and stroke risk. Primary target for treatment.',
      fallbackReferenceRange: '< 100',
      unit: 'mg/dL',
      category: 'Lipids',
      lowMeaning: 'Excellent for heart health',
      highMeaning: 'Major heart disease risk factor'
    },
    'cholestérol hdl': {
      name: 'Cholestérol HDL (Good Cholesterol)',
      description: '"Good" cholesterol that removes bad cholesterol from arteries and protects the heart.',
      clinicalSignificance: 'High levels protect against heart disease. Low levels increase cardiovascular risk.',
      fallbackReferenceRange: '> 40',
      unit: 'mg/dL',
      category: 'Lipids',
      lowMeaning: 'Increased heart disease risk',
      highMeaning: 'Protective against heart disease'
    },

    // Liver Function
    'got (asat)': {
      name: 'GOT/AST (Aspartate Aminotransferase)',
      description: 'Enzyme found in liver, heart, and muscles. Indicates liver cell damage when elevated.',
      clinicalSignificance: 'High levels suggest liver damage, heart attack, or muscle injury. Mild elevations may indicate fatty liver.',
      fallbackReferenceRange: '9 - 32',
      unit: 'IU/L',
      category: 'Liver Function',
      lowMeaning: 'Generally not significant',
      highMeaning: 'Liver damage, heart attack, or muscle injury'
    },
    'gpt (alat)': {
      name: 'GPT/ALT (Alanine Aminotransferase)',
      description: 'Liver-specific enzyme. More specific for liver damage than AST.',
      clinicalSignificance: 'High levels indicate liver cell damage from hepatitis, medications, or fatty liver disease.',
      fallbackReferenceRange: '7 - 35',
      unit: 'IU/L',
      category: 'Liver Function',
      lowMeaning: 'Generally not significant',
      highMeaning: 'Liver cell damage or disease'
    },
    'ggt': {
      name: 'GGT (Gamma-Glutamyl Transferase)',
      description: 'Enzyme that indicates bile duct problems or alcohol-related liver damage.',
      clinicalSignificance: 'High levels suggest bile duct obstruction, alcohol use, or certain medications affecting the liver.',
      fallbackReferenceRange: '10 - 50',
      unit: 'IU/L',
      category: 'Liver Function',
      lowMeaning: 'Generally not significant',
      highMeaning: 'Bile duct problems or alcohol-related liver damage'
    },

    // Inflammation
    'crp': {
      name: 'CRP (C-Reactive Protein)',
      description: 'Marker of inflammation in the body. Rises rapidly during infections or inflammatory conditions.',
      clinicalSignificance: 'High levels indicate active inflammation, infection, or increased cardiovascular risk.',
      fallbackReferenceRange: '0.00 - 0.50',
      unit: 'mg/dL',
      category: 'Inflammation',
      lowMeaning: 'Low inflammation risk',
      highMeaning: 'Active inflammation or infection'
    },

    // Thyroid Function
    'tsh ultrasensible': {
      name: 'TSH (Thyroid Stimulating Hormone)',
      description: 'Hormone that regulates thyroid function. Primary test for thyroid disorders.',
      clinicalSignificance: 'High TSH indicates hypothyroidism (underactive thyroid). Low TSH suggests hyperthyroidism (overactive thyroid).',
      fallbackReferenceRange: '0.4 - 4.5',
      unit: 'mIU/L',
      category: 'Thyroid',
      lowMeaning: 'Hyperthyroidism (overactive thyroid)',
      highMeaning: 'Hypothyroidism (underactive thyroid)'
    },
    't4 libre': {
      name: 'T4 Libre (Free T4)',
      description: 'Active thyroid hormone that regulates metabolism. Storage form of thyroid hormone.',
      clinicalSignificance: 'Low levels with high TSH confirm hypothyroidism. High levels with low TSH indicate hyperthyroidism.',
      fallbackReferenceRange: '0.8 - 1.8',
      unit: 'ng/dL',
      category: 'Thyroid',
      lowMeaning: 'Hypothyroidism symptoms',
      highMeaning: 'Hyperthyroidism symptoms'
    },
    't3 libre': {
      name: 'T3 Libre (Free T3)',
      description: 'Most active thyroid hormone. Directly affects metabolism at cellular level.',
      clinicalSignificance: 'More sensitive indicator of thyroid activity than T4. Important for tissue-level thyroid function.',
      fallbackReferenceRange: '2.3 - 4.2',
      unit: 'pg/mL',
      category: 'Thyroid',
      lowMeaning: 'Tissue-level hypothyroidism',
      highMeaning: 'Tissue-level hyperthyroidism'
    },

    // Reproductive Hormones
    'fsh': {
      name: 'FSH (Follicle Stimulating Hormone)',
      description: 'Hormone that regulates reproductive function and sperm production in men.',
      clinicalSignificance: 'High levels indicate testicular failure. Low levels suggest pituitary dysfunction.',
      fallbackReferenceRange: '1.5 - 12.4',
      unit: 'IU/L',
      category: 'Reproductive Hormones',
      lowMeaning: 'Pituitary dysfunction',
      highMeaning: 'Testicular failure or menopause'
    },
    'lh': {
      name: 'LH (Luteinizing Hormone)',
      description: 'Hormone that stimulates testosterone production in men and ovulation in women.',
      clinicalSignificance: 'Helps differentiate between primary and secondary hypogonadism.',
      fallbackReferenceRange: '1.7 - 8.6',
      unit: 'IU/L',
      category: 'Reproductive Hormones',
      lowMeaning: 'Secondary hypogonadism (pituitary problem)',
      highMeaning: 'Primary hypogonadism (testicular problem)'
    },
    '17 b oestradiol (e2)': {
      name: '17β Oestradiol (E2)',
      description: 'Primary female sex hormone, also present in men. Important for sexual development and function.',
      clinicalSignificance: 'In men, elevated levels may cause feminization. Low levels may affect libido and bone health.',
      fallbackReferenceRange: '15 - 65',
      unit: 'pg/mL',
      category: 'Reproductive Hormones',
      lowMeaning: 'May affect libido and bone health',
      highMeaning: 'May cause feminization in men'
    },
    'shbg': {
      name: 'SHBG (Sex Hormone-Binding Globulin)',
      description: 'Protein that binds sex hormones, affecting their availability. Influences free testosterone levels.',
      clinicalSignificance: 'High SHBG reduces free testosterone. Low SHBG increases free testosterone availability.',
      fallbackReferenceRange: '10 - 60',
      unit: 'nmol/L',
      category: 'Reproductive Hormones',
      lowMeaning: 'Increased free testosterone activity',
      highMeaning: 'Decreased free testosterone activity'
    },
    'testostérone totale': {
      name: 'Testostérone totale (Total Testosterone)',
      description: 'Primary male sex hormone. Essential for sexual development, muscle mass, and bone density.',
      clinicalSignificance: 'Low levels cause hypogonadism symptoms. High levels may suggest tumors or steroid use.',
      fallbackReferenceRange: '300 - 1000',
      unit: 'ng/dL',
      category: 'Reproductive Hormones',
      lowMeaning: 'Hypogonadism - low energy, muscle mass, libido',
      highMeaning: 'Possible tumors or steroid use'
    },
    'indice testostérone libre': {
      name: 'Indice testostérone libre (Free Testosterone Index)',
      description: 'Calculated measure of biologically active testosterone. More accurate than total testosterone.',
      clinicalSignificance: 'Better indicator of androgenic activity than total testosterone alone.',
      fallbackReferenceRange: '1.0 - 2.5',
      unit: 'ratio',
      category: 'Reproductive Hormones',
      lowMeaning: 'Functional hypogonadism',
      highMeaning: 'High androgenic activity'
    },

    // Stress Hormones
    'cortisol 08:00': {
      name: 'Cortisol 08:00 (Morning Cortisol)',
      description: 'Stress hormone that peaks in the morning. Essential for metabolism and stress response.',
      clinicalSignificance: 'Low levels suggest adrenal insufficiency. High levels may indicate Cushing\'s syndrome or chronic stress.',
      fallbackReferenceRange: '5 - 25',
      unit: 'μg/dL',
      category: 'Stress Hormones',
      lowMeaning: 'Adrenal insufficiency (Addison\'s disease)',
      highMeaning: 'Cushing\'s syndrome or chronic stress'
    },

    // Cancer Markers
    'psa total': {
      name: 'PSA total (Prostate-Specific Antigen)',
      description: 'Protein produced by prostate gland. Used to screen for prostate cancer and monitor prostate health.',
      clinicalSignificance: 'Elevated levels may indicate prostate cancer, enlargement, or inflammation. Requires further evaluation.',
      fallbackReferenceRange: '0.0 - 4.0',
      unit: 'ng/mL',
      category: 'Cancer Markers',
      lowMeaning: 'Low prostate cancer risk',
      highMeaning: 'Requires further prostate evaluation'
    }
  };

  getMarkerInfo(markerName: string): LabMarkerInfo | null {
    const normalizedName = markerName.toLowerCase().trim();
    return this.labMarkers[normalizedName] || null;
  }

  getAllMarkers(): { [key: string]: LabMarkerInfo } {
    return this.labMarkers;
  }

  getMarkersByCategory(category: string): LabMarkerInfo[] {
    return Object.values(this.labMarkers).filter(marker => marker.category === category);
  }

  getCategories(): string[] {
    const categories = new Set(Object.values(this.labMarkers).map(marker => marker.category));
    return Array.from(categories).sort();
  }

  // Get fallback reference range if OCR fails
  getFallbackReferenceRange(markerName: string): string | null {
    const info = this.getMarkerInfo(markerName);
    return info ? info.fallbackReferenceRange : null;
  }

  // Check if a reference range seems incomplete (for OCR validation)
  isReferenceRangeIncomplete(range: string): boolean {
    return !range || 
           range === '-' || 
           range.includes('...') || 
           range.includes('depending') ||
           range.trim().length < 3;
  }
} 