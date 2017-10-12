#include <algorithm>
#include <iostream>
#include "ngraph/log.hpp"
#include "graph_rewrite.hpp"

bool ngraph::pass::GraphRewrite::run_on_call_graph(std::list<Node*>& nodes)
{
    //until @bob implements 
};

bool ngraph::pass::GraphRewrite::run_on_call_graph(std::list<std::shared_ptr<Node>>& nodes) 
{
    bool rewritten = false;
    for (auto node : nodes)
    {
        //NGRAPH_DEBUG << "Processing " << node << std::endl;
        
        /*
        if (marked_for_replacement.find(node) != marked_for_replacement.end())
        {
            NGRAPH_INFO << "Skipping " << node << std::endl;
            continue;
        }
        */

        for (auto pair : m_matcher_callback_pairs)
        {
            
            auto matcher = pair.first;
            //NGRAPH_DEBUG << "Running matcher " << matcher << " on " << node << " , " << node->description() << std::endl;
            matcher->reset();
            if (matcher->match(node))
            {
                NGRAPH_DEBUG << "Matcher " << matcher << " matched " << node << " , " << node->description() << std::endl;
                rewritten = true;
                pair.second(matcher, node, *this);
            }
        }
    }
    return rewritten;
}

void ngraph::pass::GraphRewrite::replace_node(std::shared_ptr<Node> target, std::shared_ptr<Node> replacement) 
{
    NGRAPH_INFO << "Replacing target = " << target << " , " << target->description() << " , " <<
    "replacement = " << replacement << " , " << replacement->description() << std::endl;


    NGRAPH_DEBUG << "user = " << replacement << " , " << replacement->description() << std::endl;
    for (auto user : target->users()) 
    {
        
        auto& args = const_cast<ngraph::Nodes&>(user->get_arguments());
        auto it = std::find(begin(args), end(args), target);
        assert(it != end(args));
        //NGRAPH_DEBUG << "Replaced " << *it << " w/ " << replacement << " in args of " << user << " , args = " << &args << std::endl;
        it = args.erase(it);
        args.insert(it, replacement);
        const_cast<std::multiset<Node*> &> (replacement->users()).insert(user); 
    }

    //marked_for_replacement.insert(target); //to make sure graph traversal skips over nodes marked for replacement

    const_cast<std::multiset<Node*> &>(target->users()).clear();

    //TODO: [nikolayk] recursively walk target and update users() 
    //nodes w/ empty users sets should be DSE'ed.

}