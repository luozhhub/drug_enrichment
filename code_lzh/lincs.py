import pandas as pd
from scipy.stats import hypergeom

class lincs_data_analysis():
    def __init__(self):
        self.lincs_gene_id = set()

    def disgenet_disease_gene_list(self, disease=None):
        all_disgenet = pd.read_table("all_gene_disease_associations.tsv", sep="\t", header=0)
        gene_list_of_disease = all_disgenet[all_disgenet["diseaseId"] == disease]
        return gene_list_of_disease

    def inter_analysis(self, new_df=None, disease=None, col=None):

        down_regulated_genes = list(new_df[new_df[col] < 200].index)
        up_regulated_genes = list(new_df[new_df[col] > 12128].index)
        differential_gene_set = set(down_regulated_genes + up_regulated_genes)
        df_disgenet = self.disgenet_disease_gene_list(disease=disease)
        GDA_gene_set = set(df_disgenet["geneId"])
        disgn_in_lincs = GDA_gene_set & self.lincs_gene_id


        intersect_gene_set = differential_gene_set & GDA_gene_set

        print(col)
        print("differential list : %s" % len(differential_gene_set))
        print("disgenet list: %s" % len(disgn_in_lincs))
        print("intersect: %s" % len(intersect_gene_set))
        hypergenomic_test_p = 1 - hypergeom.cdf(len(intersect_gene_set), len(self.lincs_gene_id), len(disgn_in_lincs), len(differential_gene_set))
        print ("p value: %s" % hypergenomic_test_p)
        return hypergenomic_test_p

    def lincs_df(self, file_path=None, disease=None):
        p_df = pd.DataFrame(columns=["array_name", "p_value"])
        # read table
        df_lincs = pd.read_table(file_path, sep="\t", header=0, index_col=0)
        # entrez id list
        if len(self.lincs_gene_id) == 0:
            self.lincs_gene_id = set(df_lincs.index)

        df_lincs["mean"] = df_lincs.mean(axis=1, skipna=False)
        df_lincs_rank = df_lincs.rank()

        col_list = df_lincs.columns
        for one_col in col_list:
            p_value = self.inter_analysis(new_df=df_lincs_rank, disease=disease, col=one_col)
            p_df = p_df.append(pd.Series({"array_name":one_col, "p_value":p_value}), ignore_index=True)
        return(p_df)


if __name__ == "__main__":
    lincs_da = lincs_data_analysis()
    pvalue_df = lincs_da.lincs_df(file_path="D000544_disease_drug_cmap.txt", disease="C0002395")
    print(pvalue_df)
