import requests
from bs4 import BeautifulSoup
from collections import defaultdict 
import requests
import bs4
from bs4 import BeautifulSoup
import bisect
from llama_index.core import Document
from typing import Union, List
from collections import defaultdict 
from Intelligence.utils.misc_utils import logger, assert_
import re 

class Web_Scrapper : 
    def __init__(self, url:str = 'hello.com'):
        self.url = url.strip()
        
    def get_soup(self):
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        self.response = requests.get(self.url, headers=headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.tags = ['h1', 'h2', 'h3','h4', 'p', 'ul', 'ol', 'a', 'img', 'figcaption', 'video', 'iframe']
        self.restricted = ['read more' , 'https://', 'http://', 'www.', 'faqs' ,  
                        'about','careers', 'advertise' ,'newsletter', 'privacy policy', 'terms & condition'
                        'references', 'external links', 'see also', 'about us', 'contact us', 'bibliography']

    def scrape_blog(self):
        self.get_soup()
        # Find all the chunks of content in the blog
        self.chunks = []
        elements :List[bs4.element.Tag] = self.soup.find_all(self.tags)
        for element in elements:
            chunk = {}
            
            # If it's a figcaption
            if element.name == 'figcaption':
                chunk['type'] = 'caption'
                chunk['content'] = element.text.strip()
            
            # If it's a heading
            if element.name.startswith('h'):
                chunk['type'] = 'heading'
                chunk['content'] = element.text.strip()
            # If it's a paragraph
            elif element.name == 'p':
                chunk['type'] = 'paragraph'
                chunk['content'] = element.text.strip()
                
            # If it's an unordered list or ordered list
            elif element.name in ['ul', 'ol']:
                chunk['type'] = 'list'
                # Extract list items
                li = [li.text.strip() for li in element.find_all('li')]
                chunk['content'] = '\n- '.join(li)
                #  checking if not too many \n or \t
                for e in chunk['content']:
                    if e.count('\n') > 3 or e.count('\t') > 3:
                        continue
                        
            # If it's a hyperlink
            elif element.name == 'a':
                chunk['type'] = 'hyperlink'
                chunk['text'] = element.text.strip()
                chunk['url'] = element.get('href', '')  # Use .get() to handle missing 'href' attribute
                
            # If it's an image/ video, iframe
            elif element.name ==  'img':
                chunk['type'] = 'image'
                chunk['description'] = element.get('alt', '')   # Use .get() to handle missing 'alt' attribute
                chunk['source'] = element.get('src', '')  # Use .get() to handle missing 'src' attribute
            
            if len(chunk)>0:
                self.chunks.append(chunk)
        
        return self.chunks

    def create_dict(self):
        self.scrape_blog()
        self.blog_dict = defaultdict(list)
        
        for idx ,chunk in enumerate(self.chunks):
            try: 
                self.blog_dict[chunk['type']].append(idx)
            except KeyError:
                logger.error(f'Error in creating dict : {chunk}')
        return self.blog_dict
    
    def filter_chunks(self):
        '''
        Pattern-1 : Lists with lots of \n\n\n\n ---> represents global headings (dropping), handled in scrape_blog function.
        
        Pattern-2 : All stuff (except images) before first non-empty paragraph can be dropped.
        
        Pattern-3 : All stuff after headings (from last) like : 'References', 'External links', 'See also' can be dropped.
        '''
        self.create_dict()
            
        # Pattern-2
        start = 0
        li = self.blog_dict['paragraph']
        for idx in li:
            if self.chunks[idx]['content'] != '':
                start = idx+1
                break
        
        # Pattern-3
        end = len(self.chunks)-1
        li :list = self.blog_dict['heading']
        for i in range(len(li)-1, -1, -1):
            heading = self.chunks[li[i]]["content"].lower()
            if any(word_part in heading for word_part in self.restricted):
                continue
            else :
                end = li[i+1]-1 if i+1 < len(li) else end
                break
            
        # updating the bounds of each type of tag in self.chunks
        self.bound_dict = {}
        logger.info(f'bounds : {start} , {end}')
        for key in self.blog_dict.keys():
            li = self.blog_dict[key]
            # logger.critical(f'key : {key} , li : {li}')
            lo, hi = bisect.bisect_left(li, start) , min(bisect.bisect_right(li, end) , len(li)-1)
            self.bound_dict[key] = (lo, hi)
            
        logger.debug(f'bounds : {self.bound_dict}')
    
    
    # TODO : focus more on effective clubbing of para/lists to maintain relevancy and flow of the blog.
    def create_docs(self)->List[Document]:
        ''''
        1-) Merge the paragraphs, lists indices into a single list of indices.
        2-) Drop the headings, as they are of no use now. (may be useful for future reference in metadata)
        3-) Relatings images with the paragraphs, lists.
            - binary search to go to the images nearer to paragraph as per the orientation of the web-page.
            - Perform string matching of image name on left and right side of the paragraph.    X
        4-) Regarding Links : 
            - binary search though index of links to get to links closer to para/list.
            - Use them for key-word extraction.
            - Save them in meta-data.
        '''
        
        self.filter_chunks()
            
        combined_indices =  (self.blog_dict['paragraph'][self.bound_dict['paragraph'][0]:self.bound_dict['paragraph'][1]+1] if 'paragraph' in self.blog_dict else []) + \
                            (self.blog_dict['list'][self.bound_dict['list'][0]:self.bound_dict['list'][1]+1] if 'list' in self.blog_dict else [])
        combined_indices = self.remove_too_small_texts(sorted(combined_indices))

        img_idxs = (self.blog_dict['image'][self.bound_dict['image'][0]+2:self.bound_dict['image'][1]] if 'image' in self.blog_dict else [])
        link_idxs = (self.blog_dict['hyperlink'][self.bound_dict['hyperlink'][0]:self.bound_dict['hyperlink'][1]+1] if 'hyperlink' in self.blog_dict else [])
        caption_idxs = (self.blog_dict['caption'][self.bound_dict['caption'][0]:self.bound_dict['caption'][1]+1] if 'caption' in self.blog_dict else [])    
        
        list_of_docs = []
        for i, idx in enumerate(combined_indices):
            # getting to nearest image
            closest_img_idx = bisect.bisect_left(img_idxs, idx)
            meta_data = {}
            
            meta_data['imgs'] = []
            # checking img on left side
            if(closest_img_idx-1 >= 0):
                meta_data['imgs'].append(self.chunks[img_idxs[closest_img_idx-1]]['source'])                    
            if(closest_img_idx < len(img_idxs)):
                meta_data['imgs'].append(self.chunks[img_idxs[closest_img_idx]]['source'])
            
            # getting to nearest set of links
            lo  = bisect.bisect_left(link_idxs, idx)
            hi =  bisect.bisect_left(link_idxs, combined_indices[i+1]) if i+1 < len(combined_indices) else len(link_idxs)
            
            key_words , external_ref = [] , []
            for j in range(lo, hi):
                text:str = self.chunks[link_idxs[j]]['text'].strip()
                url : str = self.chunks[link_idxs[j]]['url']
                
                if(any(word in text.lower() for word in (self.restricted+['['])) or len(text.split())>5 or len(text)<3 or
                   (not bool(re.match(r"^(?!https?:\/\/).+", url))) or re.search(r"share on \w+" , text.lower()) or re.search(r"follow us on \w+" , text.lower())
                   ):   # ignoring the links with citation [1], [2] etc.
                    continue
                
                key_words.append(text)
                external_ref.append(url)
                
            key_words = key_words if len(key_words)<50 else key_words[:50]      # reducing no. of keywords to 50
            meta_data['imgs'] = '\n'.join(meta_data['imgs'])    
            meta_data['key_words']  = '\n'.join(key_words)
            meta_data['external_ref'] =  '\n'.join(external_ref)
            meta_data['source'] = self.url
            
            # Creating document object
            doc = Document(text= self.chunks[idx]['content'].strip() ,
                            metadata= meta_data,
                            doc_id=self.url + '_' + str(i),
                            )
            doc.excluded_llm_metadata_keys = ["external_ref" , "imgs", "source"]
            doc.excluded_embed_metadata_keys = ["external_ref" , "imgs", "source" ]
           
            list_of_docs.append(doc)

        return list_of_docs
            
            
    def remove_too_small_texts(self, combined_indices:list, word_threshold = 30):
        new_combined_indices = []
        less_words_string = ''
        for idx in combined_indices:
            n = len(self.chunks[idx]['content'].split())
            if n <3:    # ignoring such small texts
                continue
            elif n<word_threshold :
                less_words_string +=  self.chunks[idx]['content'] + '\n'    # accumulating not so small but still small texts
            else :
                if len(new_combined_indices) > 0 and less_words_string != '':   # adding the accumulated small texts to the last chunk
                    j = new_combined_indices[-1]
                    self.chunks[j]['content'] += '\n' + less_words_string
                
                self.chunks[idx]['content'] = less_words_string + '\n' + self.chunks[idx]['content']    # adding the accumulated small texts to the current chunk
                new_combined_indices.append(idx)
                less_words_string = ''
        return new_combined_indices
        
        
if __name__=='__main__':    
    scr = Web_Scrapper('https://towardsdatascience.com/transformers-141e32e69591')
    d = scr.create_docs()      
    logger.critical(d)


