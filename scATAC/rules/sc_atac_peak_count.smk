_countpeak_threads = 4

rule scatac_countpeak:
	input:
		finalpeak = "Result/Analysis/{sample}/{sample}_final_peaks.bed",
		validbarcode = "Result/QC/{sample}/{sample}_scATAC_validcells.txt",
		frag = "Result/minimap2/{sample}/fragments_corrected_count.tsv"
	output:
		count = "Result/Analysis/{sample}/{sample}_peak_count.h5"
	params:
		species = config["species"],
		outdir = "Result/Analysis/{sample}",
		outpre = "{sample}"
	threads:
		_countpeak_threads
	benchmark:
		"Result/Benchmark/{sample}_PeakCount.benchmark" 
	shell:
		"""
		MAESTRO scatac-peakcount --peak {input.finalpeak} --fragment {input.frag} --barcode {input.validbarcode} \
		--species {params.species} --cores {threads} --directory {params.outdir} --outprefix {params.outpre}
		"""