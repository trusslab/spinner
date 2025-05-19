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
You will need to build a linux kernel from source with BTF information included. You will also need to build and install libbpf. Finally you will need to generate vmlinux.bc for the kernel you wish to test. The instructions for doing this are beyond the scope of this document.

Steps to run:
1) First install necessary dependencies:
	./install_dependencies.sh
2) Run context analysis:
	./run_selftests.sh path/to/kernel/source
3) Run API analysis:
	./run_fptests.sh path/to/kernel/source 
4) Generate callgraph:
	cd mlta
	<write the path to your vmlinux.bc file in bc.list>
	cd ..
	./run_mlta.sh 
5) Generate bug reports:
	./run_graphtraverse.sh path/to/callgraph


Automated Testing of Reports:

