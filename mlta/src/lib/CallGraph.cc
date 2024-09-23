//===-- CallGraph.cc - Build global call-graph------------------===//
// 
// This pass builds a global call-graph. The targets of an indirect
// call are identified based on type-analysis, i.e., matching the
// number and type of function parameters.
//
//===-----------------------------------------------------------===//

#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h" 
#include "llvm/IR/Instruction.h"
#include "llvm/IR/GlobalValue.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Support/Debug.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Constants.h"
#include "llvm/ADT/StringExtras.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Support/raw_ostream.h"  
#include "llvm/IR/InstrTypes.h" 
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h" 
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/CFG.h" 

#include "Common.h"
#include "CallGraph.h"

#include <map> 
#include <vector> 

#include <stdio.h>

#include <iostream>
#include <fstream>

using namespace llvm;
using namespace std;
fstream dotfile;
vector<string> added;

//
// Implementation
//

void CallGraphPass::doMLTA(Function *F) {
 	
  // Unroll loops
#ifdef UNROLL_LOOP_ONCE
  unrollLoops(F);
#endif
  // Collect callers and callees
  for (inst_iterator i = inst_begin(F), e = inst_end(F);
			i != e; ++i) {
		// Map callsite to possible callees.
		if (CallInst *CI = dyn_cast<CallInst>(&*i)) {

			CallSet.insert(CI);

			FuncSet *FS = &Ctx->Callees[CI];
			Value *CV = CI->getCalledOperand();
			Function *CF = dyn_cast<Function>(CV);
			Function *Parent = CI->getCaller();	
			//dotfile<<Parent->getGUID(Parent->getGlobalIdentifier())<<"->";
			//OP<<Parent->getName().str()<<"\n";
			//dotfile<<Parent->getName().str()<<"\n";
			
			// Indirect call
			if (CI->isIndirectCall()) {

				// Multi-layer type matching
				if (ENABLE_MLTA > 1) {
					findCalleesWithMLTA(CI, *FS);
				}
				// Fuzzy type matching
				else if (ENABLE_MLTA == 0) {
					size_t CIH = callHash(CI);
					if (MatchedICallTypeMap.find(CIH)
							!= MatchedICallTypeMap.end())
						*FS = MatchedICallTypeMap[CIH];
					else {
						findCalleesWithType(CI, *FS);
						MatchedICallTypeMap[CIH] = *FS;
					}
				}
				// One-layer type matching
				else {
					*FS = Ctx->sigFuncsMap[callHash(CI)];
				}

#ifdef MAP_CALLER_TO_CALLEE
				for (Function *Callee : *FS) {
					Ctx->Callers[Callee].insert(CI);
					
				}
#endif
				// Save called values for future uses.
				Ctx->IndirectCallInsts.push_back(CI);

				ICallSet.insert(CI);
				if (!FS->empty()) {
					MatchedICallSet.insert(CI);
					Ctx->NumIndirectCallTargets += FS->size();
					Ctx->NumValidIndirectCalls++;
				}
			}
			// Direct call
			else {
				// not InlineAsm
				if (CF) {
					// Call external functions
					if (CF->isDeclaration()) {
						if (Function *GF = Ctx->GlobalFuncMap[CF->getGUID()])
							CF = GF;
					}

					FS->insert(CF);
					//callgraph for only direct calls
					dotfile<<"Node"<<Parent->getGUID(Parent->getGlobalIdentifier())<<" -> ";
                                	dotfile<<"Node"<<CF->getGUID(CF->getGlobalIdentifier())<<"[color=black];"<<"\n";
#ifdef MAP_CALLER_TO_CALLEE
					Ctx->Callers[CF].insert(CI);

#endif
				}
				// InlineAsm
				else {
					// TODO: handle InlineAsm functions
				}
			}

			//generateCallgraph(*FS, F);
			for (Function *Callee: *FS) {
				//uncomment next two lines for callgraph with indirect and direct calls
				//dotfile<<"Node"<<Parent->getGUID(Parent->getGlobalIdentifier())<<" -> ";
				//dotfile<<"Node"<<Callee->getGUID(Callee->getGlobalIdentifier())<<"[color=black];"<<"\n";
				
				/*
				if (find(added.begin(), added.end(),Callee->getName().str())!=added.end()){
					dotfile<<"Node"<<Callee->getGUID(Callee->getGlobalIdentifier())<<" [shape=record, label=\"{fun: "<<Callee->getName().str()<<"}\"];\n";
				}
				*/
				//dotfile<<"Caller: "<<Parent->getName().str()<<" Callee: "<<Callee->getName().str()<<"\n";
			}
			//end

			if (ENABLE_MLTA > 1) {
				if (CI->isIndirectCall()) {

#ifdef PRINT_ICALL_TARGET
					printSourceCodeInfo(CI, "RESOLVING");
#endif

					//FuncSet FSBase = Ctx->sigFuncsMap[callHash(CI)];
					//if (LayerNo > 0) {
					for (auto F : Ctx->sigFuncsMap[callHash(CI)]) {
						if (FS->find(F) == FS->end()) {
#ifdef PRINT_ICALL_TARGET
							if ((OutScopeFuncs.find(F) == OutScopeFuncs.end())
									&& (StoredFuncs.find(F) != StoredFuncs.end())) {
								printSourceCodeInfo(F, "REMOVED");
							}
							else {
							}
#endif
						}
					}
#ifdef PRINT_ICALL_TARGET
					printTargets(*FS, CI);
#endif
				}
				}
			}
		}
	}

bool CallGraphPass::doInitialization(Module *M) {
	OP<<"#"<<MIdx<<" Initializing: "<<M->getName()<<"\n";

	++ MIdx;

	DLMap[M] = &(M->getDataLayout());
	Int8PtrTy[M] = Type::getInt8PtrTy(M->getContext());
	IntPtrTy[M] = DLMap[M]->getIntPtrType(M->getContext());

	set<User *>CastSet;

	//
	// Iterate and process globals
	//
	for (Module::global_iterator gi = M->global_begin(); 
			gi != M->global_end(); ++gi) {

		GlobalVariable* GV = &*gi;
		if (GV->hasInitializer()) {

			Type *ITy = GV->getInitializer()->getType();
			if (!ITy->isPointerTy() && !isCompositeType(ITy))
				continue;

			Ctx->Globals[GV->getGUID()] = GV;

			typeConfineInInitializer(GV);
		}
	}

	// Iterate functions and instructions
	for (Function &F : *M) { 

		// Collect address-taken functions.
		// NOTE: declaration functions can also have address taken 
		if (F.hasAddressTaken()) {
			Ctx->AddressTakenFuncs.insert(&F);
			size_t FuncHash = funcHash(&F, false);
			Ctx->sigFuncsMap[FuncHash].insert(&F);
			StringRef FName = F.getName();
      if (FName.startswith("__x64") ||
          FName.startswith("__ia32")) {
        OutScopeFuncs.insert(&F);
      }
		}

		// The following only considers actual functions with body
		if (F.isDeclaration()) {
			continue;
		}

		collectAliasStructPtr(&F);
		typeConfineInFunction(&F);
		typePropInFunction(&F);

		// Collect global function definitions.
		if (F.hasExternalLinkage()) {
			Ctx->GlobalFuncMap[F.getGUID()] = &F;
		}
	}

	// Do something at the end of last module
	if (Ctx->Modules.size() == MIdx) {

		// Map the declaration functions to actual ones
		// NOTE: to delete an item, must iterate by reference
		for (auto &SF : Ctx->sigFuncsMap) {
			for (auto F : SF.second) {
				if (!F)
					continue;
				if (F->isDeclaration()) {
					SF.second.erase(F);
					if (Function *AF = Ctx->GlobalFuncMap[F->getGUID()]) {
						SF.second.insert(AF);
					}
				}
			}
		}

		for (auto &TF : typeIdxFuncsMap) {
			for (auto &IF : TF.second) {
				for (auto F : IF.second) {
					if (F->isDeclaration()) {
						IF.second.erase(F);
						if (Function *AF = Ctx->GlobalFuncMap[F->getGUID()]) {
							IF.second.insert(AF);
						}
					}
				}
			}
		}

		MIdx = 0;
	}

	return false;
}

bool CallGraphPass::doFinalization(Module *M) {
		++ MIdx;
	

	if (Ctx->Modules.size() == MIdx) {
		// Finally map declaration functions to actual functions
		OP<<"Mapping declaration functions to actual ones...\n";
		Ctx->NumIndirectCallTargets = 0;
		for (auto CI : CallSet) {
			FuncSet FS;
			for (auto F : Ctx->Callees[CI]) {
				if (F->isDeclaration()) {
					F = Ctx->GlobalFuncMap[F->getGUID()];
					if (F) {
						FS.insert(F);
					}
				}
				else
					FS.insert(F);
			}
			Ctx->Callees[CI] = FS;
			if (CI->isIndirectCall()) {
				Ctx->NumIndirectCallTargets += FS.size();
				//printTargets(Ctx->Callees[CI], CI);
			}
		}

	}
	return false;
}

bool CallGraphPass::doModulePass(Module *M) {
	dotfile.open("src/lib/callgraph.dot");
  	dotfile<<"digraph \"Call Graph\"  {\n";
	OP<<"dotfile opened\n";
	++ MIdx;

	//
	// Iterate and process globals
	//
	for (Module::global_iterator gi = M->global_begin(); 
			gi != M->global_end(); ++gi) {

		GlobalVariable* GV = &*gi;
		//if (GV->user_empty())
		//	continue;

		Type *GTy = GV->getType();
		assert(GTy->isPointerTy());

	}
	if (MIdx == Ctx->Modules.size()) {
	}

	//
	// Process functions
	//
	for (Module::iterator f = M->begin(), fe = M->end(); 
			f != fe; ++f) {

		Function *F = &*f;

		if (F->isDeclaration())
			continue;
		dotfile<<"Node"<<F->getGUID(F->getGlobalIdentifier())<<" [shape=record, label=\"{fun: "<<F->getName().str()<<"}\"];\n";
		//added.push_back(F->getName().str());
		doMLTA(F);
	}
	dotfile<<"}";
	dotfile.close();
	OP<<"dotfile closed \n";
	return false;
}

