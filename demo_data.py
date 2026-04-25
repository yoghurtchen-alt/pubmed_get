"""
演示数据模块
用于离线测试和演示程序功能
"""


def get_demo_articles(query: str = "demo") -> list:
    """获取演示文献数据"""
    return [
        {
            "pmid": "38012345",
            "title": "Novel Therapeutic Approaches for Type 2 Diabetes Mellitus: A Comprehensive Review",
            "abstract": "Background: Type 2 diabetes mellitus (T2DM) is a chronic metabolic disorder characterized by insulin resistance and progressive beta-cell dysfunction. Despite existing therapeutic options, many patients fail to achieve adequate glycemic control. Objective: This review summarizes novel therapeutic approaches for T2DM management, including emerging pharmacological agents and non-pharmacological interventions. Methods: We conducted a comprehensive literature search of PubMed, Embase, and Cochrane Library databases from 2020 to 2024. Results: Several novel drug classes show promising results, including dual GIP/GLP-1 receptor agonists, SGLT2 inhibitors with additional cardiovascular benefits, and emerging gene therapy approaches. Non-pharmacological interventions such as personalized nutrition and digital health technologies also demonstrate significant potential. Conclusion: The therapeutic landscape for T2DM is rapidly evolving, with multiple promising approaches in development that may improve patient outcomes.",
            "authors": ["Zhang L", "Wang H", "Chen Y", "Liu X", "Li J"],
            "first_author": "Zhang L",
            "journal": "Diabetes Care",
            "pub_date": "2024-01-15",
            "year": "2024",
            "doi": "10.2337/dc23-1234",
            "keywords": ["diabetes mellitus", "therapeutics", "GLP-1 agonists", "SGLT2 inhibitors"],
            "mesh_terms": ["Diabetes Mellitus, Type 2", "Hypoglycemic Agents", "Glucagon-Like Peptide 1"],
            "publication_types": ["Journal Article", "Review"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/38012345/"
        },
        {
            "pmid": "37987654",
            "title": "Cardiovascular Outcomes of SGLT2 Inhibitors in Patients with Heart Failure: Meta-Analysis",
            "abstract": "Background: Sodium-glucose cotransporter 2 (SGLT2) inhibitors have shown cardiovascular benefits in patients with type 2 diabetes, but their effects in heart failure patients without diabetes remain unclear. Methods: We performed a systematic review and meta-analysis of randomized controlled trials comparing SGLT2 inhibitors with placebo in heart failure patients. Results: Pooled analysis of 8 trials (n=15,843) demonstrated that SGLT2 inhibitors significantly reduced the risk of cardiovascular death or hospitalization for heart failure (HR 0.74, 95% CI 0.68-0.80). Benefits were consistent across diabetes status, ejection fraction, and baseline renal function. Conclusion: SGLT2 inhibitors provide robust cardiovascular protection in heart failure patients regardless of diabetes status.",
            "authors": ["Smith JR", "Johnson AB", "Williams CD"],
            "first_author": "Smith JR",
            "journal": "New England Journal of Medicine",
            "pub_date": "2023-11-20",
            "year": "2023",
            "doi": "10.1056/NEJMoa2304567",
            "keywords": ["SGLT2 inhibitors", "heart failure", "cardiovascular outcomes", "meta-analysis"],
            "mesh_terms": ["Sodium-Glucose Transporter 2 Inhibitors", "Heart Failure", "Cardiovascular Diseases"],
            "publication_types": ["Journal Article", "Meta-Analysis"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37987654/"
        },
        {
            "pmid": "37890123",
            "title": "Artificial Intelligence in Medical Diagnosis: Current Applications and Future Directions",
            "abstract": "Artificial intelligence (AI) has emerged as a transformative technology in healthcare, with particular promise in medical diagnosis. This review examines current applications of AI in diagnostic medicine, including medical imaging analysis, pathology, and clinical decision support systems. We discuss deep learning algorithms for radiological image interpretation, natural language processing for electronic health records, and machine learning models for predictive diagnostics. Challenges including data quality, algorithm bias, regulatory approval, and clinical integration are addressed. Future directions include federated learning, explainable AI, and multimodal diagnostic systems. While AI shows great potential to augment clinical decision-making, careful implementation and ongoing validation are essential to ensure patient safety and diagnostic accuracy.",
            "authors": ["Brown KM", "Davis RL", "Miller TJ", "Wilson AP"],
            "first_author": "Brown KM",
            "journal": "Nature Medicine",
            "pub_date": "2023-09-10",
            "year": "2023",
            "doi": "10.1038/s41591-023-02567-8",
            "keywords": ["artificial intelligence", "machine learning", "medical diagnosis", "deep learning"],
            "mesh_terms": ["Artificial Intelligence", "Diagnosis", "Machine Learning", "Deep Learning"],
            "publication_types": ["Journal Article", "Review"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37890123/"
        },
        {
            "pmid": "37765432",
            "title": "Long-term Efficacy of mRNA COVID-19 Vaccines in Immunocompromised Patients",
            "abstract": "Objective: To evaluate the long-term efficacy and safety of mRNA COVID-19 vaccines in immunocompromised patient populations. Design: Prospective cohort study. Setting: Multi-center study across 15 hospitals. Participants: 2,456 immunocompromised patients including solid organ transplant recipients, patients with autoimmune diseases on immunosuppressive therapy, and hematological malignancy patients. Main Outcome Measures: Vaccine effectiveness against severe COVID-19, breakthrough infection rates, and adverse events at 12-month follow-up. Results: Vaccine effectiveness against severe disease was 68.5% (95% CI 61.2-74.5%) at 12 months, lower than immunocompetent controls (89.2%). Booster doses significantly improved protection. No serious vaccine-related adverse events were observed. Conclusions: mRNA vaccines provide moderate long-term protection in immunocompromised patients, with boosters enhancing efficacy.",
            "authors": ["Anderson PL", "Thompson SK", "Garcia MR", "Lee JH"],
            "first_author": "Anderson PL",
            "journal": "The Lancet",
            "pub_date": "2023-07-05",
            "year": "2023",
            "doi": "10.1016/S0140-6736(23)01234-5",
            "keywords": ["COVID-19", "mRNA vaccines", "immunocompromised", "vaccine efficacy"],
            "mesh_terms": ["COVID-19", "mRNA Vaccines", "Immunocompromised Host", "Vaccine Efficacy"],
            "publication_types": ["Journal Article", "Multicenter Study"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37765432/"
        },
        {
            "pmid": "37654321",
            "title": "Precision Medicine in Oncology: Genomic Profiling and Targeted Therapy Selection",
            "abstract": "Precision medicine has revolutionized oncology by enabling treatment selection based on individual tumor molecular profiles. This study presents a comprehensive analysis of 5,000 cancer patients who underwent comprehensive genomic profiling. Actionable mutations were identified in 42% of patients, leading to targeted therapy recommendations. Response rates to matched targeted therapies were significantly higher than unmatched treatments (58% vs 23%, p<0.001). Key findings include novel fusion events, resistance mechanisms, and biomarker-driven treatment strategies. The study demonstrates the clinical utility of comprehensive genomic profiling in guiding precision oncology treatment decisions and improving patient outcomes.",
            "authors": ["White SJ", "Roberts MN", "Taylor KL", "Harris PD", "Clark EF"],
            "first_author": "White SJ",
            "journal": "Journal of Clinical Oncology",
            "pub_date": "2023-05-18",
            "year": "2023",
            "doi": "10.1200/JCO.23.00456",
            "keywords": ["precision medicine", "oncology", "genomic profiling", "targeted therapy"],
            "mesh_terms": ["Precision Medicine", "Neoplasms", "Genomic Profiling", "Molecular Targeted Therapy"],
            "publication_types": ["Journal Article", "Research Support, Non-U.S. Gov't"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37654321/"
        },
        {
            "pmid": "37543210",
            "title": "Microbiome Dysbiosis and Inflammatory Bowel Disease: Mechanistic Insights",
            "abstract": "The gut microbiome plays a crucial role in the pathogenesis of inflammatory bowel disease (IBD). This review synthesizes current evidence on microbiome alterations in Crohn's disease and ulcerative colitis. Key findings include reduced bacterial diversity, altered Firmicutes/Bacteroidetes ratio, and enrichment of pro-inflammatory species. Mechanistic studies reveal impaired mucosal barrier function, dysregulated immune responses, and altered microbial metabolite production. Therapeutic implications include fecal microbiota transplantation, probiotics, and microbiome-targeted dietary interventions. Future research directions focus on personalized microbiome modulation strategies and integration of multi-omics approaches for IBD management.",
            "authors": ["Martin CH", "Lewis DK", "Walker JR"],
            "first_author": "Martin CH",
            "journal": "Gastroenterology",
            "pub_date": "2023-03-22",
            "year": "2023",
            "doi": "10.1053/j.gastro.2023.01.045",
            "keywords": ["microbiome", "inflammatory bowel disease", "Crohn disease", "ulcerative colitis"],
            "mesh_terms": ["Microbiota", "Inflammatory Bowel Diseases", "Crohn Disease", "Colitis, Ulcerative"],
            "publication_types": ["Journal Article", "Review"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37543210/"
        },
        {
            "pmid": "37432109",
            "title": "Remote Patient Monitoring in Chronic Disease Management: Systematic Review",
            "abstract": "Background: Remote patient monitoring (RPM) technologies have gained prominence in chronic disease management, particularly following the COVID-19 pandemic. Objective: To systematically evaluate the effectiveness of RPM interventions across various chronic conditions. Methods: Systematic review and meta-analysis of randomized controlled trials published 2018-2023. Results: 45 trials (n=12,847 patients) were included. RPM significantly improved disease control metrics (standardized mean difference 0.42, 95% CI 0.28-0.56), reduced hospitalizations (RR 0.78), and enhanced patient satisfaction. Benefits were observed across diabetes, hypertension, heart failure, and chronic obstructive pulmonary disease. Conclusion: RPM is an effective adjunct to standard care for chronic disease management.",
            "authors": ["Young AB", "King SL", "Wright PR", "Green TL"],
            "first_author": "Young AB",
            "journal": "BMJ",
            "pub_date": "2023-01-30",
            "year": "2023",
            "doi": "10.1136/bmj-2022-071234",
            "keywords": ["remote patient monitoring", "chronic disease", "telemedicine", "systematic review"],
            "mesh_terms": ["Remote Consultation", "Chronic Disease", "Telemedicine", "Patient Monitoring"],
            "publication_types": ["Journal Article", "Systematic Review", "Meta-Analysis"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37432109/"
        },
        {
            "pmid": "37321098",
            "title": "Neuroprotective Effects of Exercise in Alzheimer's Disease: Clinical and Preclinical Evidence",
            "abstract": "Physical exercise has emerged as a promising non-pharmacological intervention for Alzheimer's disease (AD). This comprehensive review examines clinical and preclinical evidence for exercise-induced neuroprotection in AD. Mechanistic studies demonstrate exercise-mediated reduction of amyloid-beta deposition, tau phosphorylation, and neuroinflammation. Clinical trials show improved cognitive function, reduced brain atrophy, and enhanced cerebral blood flow in exercising AD patients. Optimal exercise parameters including intensity, duration, and type are discussed. The review highlights molecular pathways involving BDNF, IGF-1, and vascular endothelial growth factor. Exercise represents a safe, cost-effective intervention with disease-modifying potential in AD.",
            "authors": ["Hall MN", "Allen KP", "Scott JR", "Adams LQ"],
            "first_author": "Hall MN",
            "journal": "Neurology",
            "pub_date": "2022-11-15",
            "year": "2022",
            "doi": "10.1212/WNL.0000000000201456",
            "keywords": ["Alzheimer disease", "exercise", "neuroprotection", "cognitive function"],
            "mesh_terms": ["Alzheimer Disease", "Exercise", "Neuroprotective Agents", "Cognitive Dysfunction"],
            "publication_types": ["Journal Article", "Review"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/37321098/"
        }
    ]
