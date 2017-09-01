import urllib
import ssl
context=ssl._create_unverified_context()
from PIL import Image,ImageDraw
import itertools
from bisect import bisect_left
def G5NR_image(variable,yyyymmddhh,lat,lon,dlat,dlon,tag={'None':None},out_directory=None):
    def frange(start, end, num_of_elements):
        delta=float(end-start)/(num_of_elements-1)
        newend=end+delta
        retl=start
        while retl < newend :
            yield retl
            retl += delta
    def getUrl(yyyymmddhhmm,variable):    
        baseurl="https://g5nr.nccs.nasa.gov/static/naturerun/fimages"
        d="/"

        stringList=[baseurl,variable.upper(),"Y"+yyyymmddhhmm[0:4],"M"+yyyymmddhhmm[4:6],"D"+yyyymmddhhmm[6:8]]
        stringList+=[variable.lower()+"_globe_c1440_NR_BETA9-SNAP_"+yyyymmddhhmm[0:8]+"_"+yyyymmddhhmm[8:]+"z.png"]
        url=d.join(stringList)
        return url
    def gendrawpts(cx,cy,piz=2):
        return itertools.product(xrange(cx-piz,cx+piz+1),xrange(cy-piz,cy+piz+1))
    
    url=getUrl(yyyymmddhh,variable)

    context=ssl._create_unverified_context()

    print(url)
    try:
        f=urllib.urlopen(url,context=context)
        oimg=Image.open(f)#.copy()
        size=oimg.size
    except IOError:
        return url+' Not available '

    
    lats=list(frange(-90,90,size[1]))#[::-1]
    lons=list(frange(-17.5,342.5,size[0]))
 
    if lon-dlon<-17.5 or lon+dlon>342.5:
        new_im = Image.new('RGB', (size[0],size[1]))
        x_offset = 0
        xind=bisect_left(lons,180)
        #print(lons[xind])
        images=[oimg.crop((xind,0,size[0],size[1])),oimg.crop((0,0,xind-1,size[1]))]
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        oimg.close()
        oimg=new_im
        
        lons=list(frange(-180.0,180.0,size[0]))
        
        if lon>180.0: 
            lon=lon-360.0

    lon_st=bisect_left(lons,lon-dlon) #lons.index(180.09186864738234)
    lon_ct=bisect_left(lons,lon)
    lon_en=bisect_left(lons,min(lon+dlon,342.5))
    
    lat_en=size[1]-(bisect_left(lats,max(lat-dlat,-90.0))+1)
    lat_ct=size[1]-(bisect_left(lats,lat)+1)
    lat_st=size[1]-(bisect_left(lats,min(lat+dlat,90.0))+1)
    
    dw=ImageDraw.Draw(oimg)
    dw.point(list(gendrawpts(lon_ct,lat_ct,5)),'Red')
    
    cpd_img=oimg.crop((lon_st,lat_st,lon_en,lat_en))
    oimg.close()
    outfile=variable+'_'+tag.keys()[0]+'_'+"{0:.1f}".format(tag.values()[0])+'_lat_'+"{0:.1f}".format(lat)+'_lon_'+"{0:.1f}".format(lon)+'_'+str(yyyymmddhh)+'.png'
    if not out_directory:
        cpd_img.save(outfile)
    else:
        cpd_img.save(str(out_directory)+outfile)
    return outfile 
if __name__=='__main__':
   G5NR_image('cloudsvis','200506010930',10,72,10,20,{'skedot':2.1},out_directory="./cloudsvis/")
   #import concurrent
   #import datetime
   #p=concurrent.futures.ProcessPoolExecutor()
   #ex=concurrent.futures.ProcessPoolExecutor(max_workers=2)
   #g=ex.map(make_case,gl,chunk_size=1)
   #st=datetime.datetime.now()
   #list(g)
   #print(datetime.datetime.now()-st).total_seconds()
   #ex.shutdown()
