# Spinner

This tool attempts to find deadlock bugs in the eBPF runtime. The following steps are performed by the tool:
1) Dynamic analysis to find relevant information needed to detect deadlock bugs. 
	1.1) Context Analysis using eBPF selftests
	1.2) API analysis using eBPF verifier
2) Callgraph Generation using MLTA
3) Static Analysis to detect deadlock bugs
Optional:
4) Automated testing of reports generated in step 3 using S2E symbolic analysis.

Requirements:
You will need to build a linux kernel from source with BTF information included. You will also need to install the kernel headers. Next you will need to build and install libbpf and bpftool. 
Finally you will need to generate vmlinux.bc for the kernel you wish to test. The instructions for doing this are beyond the scope of this document.

Note: It is recommended to use this tool within a VM to prevent breaking anything.

Steps to run:
1) First install necessary dependencies:
	./install_dependencies.sh
	cd mlta
	./build-llvm.sh
2) Run context analysis:
	./run_selftests.sh path/to/kernel/source
3) Run API analysis:
	./run_fptests.sh path/to/kernel/source 
	You might want to look at any errors at this point. These could indicate some unsatisfied requirements that could affect the accuracy of the analysis. 
4) Generate callgraph:
	cd mlta
	<write the path to your vmlinux.bc file in bc.list>
	cd ..
	./run_mlta.sh 
The generated callgraph should be found in mlta/callgraph.dot
5) Generate bug reports:
	./run_graphtraverse.sh path/to/callgraph


Automated Testing of Reports:

